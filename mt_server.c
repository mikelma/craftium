// my_extension.c
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h> // read(), write(), close()
#include <poll.h>

#define SA struct sockaddr

static PyObject* init_server(PyObject* self, PyObject* args) { // , PyObject* args) {
  int port, sockfd, connfd;
  struct sockaddr_in servaddr;

  // socket create and verification
  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd == -1) {
    PyErr_SetString(PyExc_Exception, "Server socket creation failed");
    return NULL;
  }

  bzero(&servaddr, sizeof(servaddr));

  // Assign IP and port
  servaddr.sin_family = AF_INET;
  servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
  servaddr.sin_port = htons(0);

  // Binding newly created socket to given address
  if ((bind(sockfd, (SA*)&servaddr, sizeof(servaddr))) != 0) {
    PyErr_SetString(PyExc_Exception, "Server socket bind failed");
    return NULL;
  }

  struct sockaddr_in sin;
  socklen_t len = sizeof(sin);
  if (getsockname(sockfd, (struct sockaddr *)&sin, &len) == -1) {
    PyErr_SetString(PyExc_Exception, "Server socket getsockname failed");
    return NULL;
  }

  port = ntohs(sin.sin_port);

  PyObject *py_port = Py_BuildValue("i", port);
  PyObject *py_sockfd = Py_BuildValue("i", sockfd);
  return PyTuple_Pack(2, py_port, py_sockfd);
}

static PyObject* server_listen(PyObject* self, PyObject* args) {
  int sockfd, connfd, len, res, timeout_ms;
  struct sockaddr_in cli;
  struct pollfd pfd;

  if (!PyArg_ParseTuple(args, "ii", &sockfd, &timeout_ms)) {
    PyErr_SetString(PyExc_TypeError, "Expected two integers as arguments: sockefd, and timeout_ms");
    return NULL;
  }

  if ((listen(sockfd, 1)) != 0) {
    PyErr_SetString(PyExc_Exception, "Server socket listen failed");
    return NULL;
  }

  pfd.fd = sockfd;
  pfd.events = POLLIN;
  pfd.revents = 0;

  if ((res = poll(&pfd, 1, timeout_ms)) <= 0) {
    if (res < 0)
      PyErr_SetString(PyExc_Exception, "Server socket poll failed");
    else
      PyErr_SetString(PyExc_ConnectionError, "Server socket listen timeout reached");
    return NULL;
  }

  len = sizeof(cli);
  connfd = accept(sockfd, (SA*)&cli, &len);
  if (connfd < 0) {
    PyErr_SetString(PyExc_Exception, "Server socket accept failed");
    return NULL;
  }

  return Py_BuildValue("i", connfd); // return connection's fd
}


static PyObject* server_recv(PyObject* self, PyObject* args) {
  int connfd, n_bytes, obs_width, obs_height, n_read;
  double reward;
  char *buff;

  if (!PyArg_ParseTuple(args, "iiii", &connfd, &n_bytes, &obs_width, &obs_height)) {
    PyErr_SetString(PyExc_TypeError,
                    "Arguments must be 4 integers: connection's fd, num. of bytes to read, obs. width, and obs. height.");
    return NULL;
  }

  // Create the buffer where the received image+data will be stored
  buff = (char*)malloc(n_bytes);
  if (buff == NULL) {
    PyErr_SetString(PyExc_Exception, "Failed to allocate memory for recv buffer");
    return NULL;
  }

  n_read = read(connfd, buff, n_bytes);
  if (n_read <= 0) {
    PyErr_SetString(PyExc_ConnectionError, "Failed to receive from MT");
    return NULL;
  }

  // Retreive the termination flag (last byte in the buffer) and reward (8 bytes)
  int termination = (int) buff[n_bytes-1];
  PyObject* py_termination = PyBool_FromLong(termination);

  memcpy(&reward, &buff[n_bytes-9], sizeof(reward));
  PyObject* py_reward = PyFloat_FromDouble(reward);

  // Create the numpy array of the image
  npy_intp dims[3] = {obs_width, obs_height, 3};
  PyObject* array = PyArray_SimpleNewFromData(3, dims, NPY_UINT8, buff);
  if (!array) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to create NumPy array");
    return NULL;
  }

  // Make the NumPy array own its data.
  // This makes sure that NumPy handles the data lifecycle properly.
  PyArray_ENABLEFLAGS((PyArrayObject*)array, NPY_ARRAY_OWNDATA);

  PyObject* tuple = PyTuple_Pack(3, array, py_reward, py_termination);

  // Decreases the reference count of Python objects. Useful if the
  // objects' lifetime is no longer needed after creating the tuple.
  Py_DECREF(array);
  Py_DECREF(py_reward);
  Py_DECREF(py_termination);

  return tuple;
}

static PyObject* server_send(PyObject* self, PyObject* args) {
  int connfd, n_send, size;
  PyObject *bytes_obj;
  char *buff;

  if (!PyArg_ParseTuple(args, "iS", &connfd, &bytes_obj)) {
    PyErr_SetString(PyExc_TypeError,
                    "Arguments are: connection's fd (int), and a bytes object.");
    return NULL;
  }

  // Get the size of the bytes object
  size = PyBytes_Size(bytes_obj);
  if (size < 0) {
    return NULL;
  }

  // Get a pointer to the bytes object's data
  buff = PyBytes_AsString(bytes_obj);
  if (buff == NULL) {
    return NULL;
  }

  n_send = write(connfd, buff, size);
  if (n_send <= 0) {
    PyErr_SetString(PyExc_ConnectionError, "Failed to send data to MT");
    return NULL;
  }
  return Py_BuildValue("");
}

// Method definitions
static PyMethodDef MyMethods[] = {
    {"init_server", init_server, METH_VARARGS, "Initialize the MT server"},
    {"server_listen", server_listen, METH_VARARGS, "Listen for MT to connect"},
    {"server_recv", server_recv, METH_VARARGS, "Receive message from MT"},
    {"server_send", server_send, METH_VARARGS, "Sends a message to MT"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef mymodule = {
    PyModuleDef_HEAD_INIT,
    "mt_server",
    "A fast implementation for the MT communication server",
    -1,
    MyMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_mt_server(void) {
    PyObject *m;
    m = PyModule_Create(&mymodule);
    if (m == NULL) {
        return NULL;
    }
    import_array();  // Initialize NumPy API
    return m;
}
