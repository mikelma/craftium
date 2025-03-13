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
#include <msgpack.h>

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

#define BUFFER_SIZE 8192

int read_large_from_socket(int socket_fd, char *buffer, int total_size) {
    int bytes_received = 0;
    int total_bytes = 0;

    while (total_bytes < total_size) {
        // Calculate remaining size to read
        int bytes_to_read = (total_size - total_bytes) < BUFFER_SIZE ?
                            (total_size - total_bytes) : BUFFER_SIZE;

        bytes_received = recv(socket_fd, buffer + total_bytes, bytes_to_read, 0);

        if (bytes_received < 0) {
            // Handle error
            if (errno == EINTR) {
                continue;  // Interrupted by signal, retry recv
            } else {
                perror("recv failed");
                return -1;  // Indicate failure
            }
        } else if (bytes_received == 0) {
            // Connection closed by peer
            break;
        }
        total_bytes += bytes_received;
    }
    return total_bytes;
}

static PyObject* python_dict_from_msgpack_map(msgpack_object_map map);

static PyObject* python_list_from_msgpack_array(msgpack_object_array array){
  PyObject* py_list = PyList_New(array.size);

  for (size_t i = 0; i < array.size; i++) {
    msgpack_object elem = array.ptr[i];
    
    if (elem.type == MSGPACK_OBJECT_BOOLEAN){
      PyList_SetItem(py_list, i, PyBool_FromLong(elem.via.boolean)); 
    } else if (elem.type == MSGPACK_OBJECT_POSITIVE_INTEGER){
      PyList_SetItem(py_list, i, PyLong_FromUnsignedLongLong(elem.via.u64));
    } else if (elem.type == MSGPACK_OBJECT_NEGATIVE_INTEGER){
      PyList_SetItem(py_list, i, PyLong_FromLongLong(elem.via.i64));
    } else if(elem.type == MSGPACK_OBJECT_FLOAT32){
      PyList_SetItem(py_list, i, PyFloat_FromDouble(elem.via.f64));
    } else if(elem.type == MSGPACK_OBJECT_FLOAT64){
      PyList_SetItem(py_list, i, PyFloat_FromDouble(elem.via.f64));
    } else if (elem.type == MSGPACK_OBJECT_STR){
      char *elem_str = strndup(elem.via.str.ptr, elem.via.str.size);
      PyList_SetItem(py_list, i, PyUnicode_FromString(elem_str));
      free(elem_str);
    } else if (elem.type == MSGPACK_OBJECT_ARRAY){
      PyObject* elem_py_list = python_list_from_msgpack_array(elem.via.array);
      PyList_SetItem(py_list, i, elem_py_list);
      Py_DECREF(elem_py_list);    
    } else if (elem.type == MSGPACK_OBJECT_MAP){
      PyObject* elem_py_dict = python_dict_from_msgpack_map(elem.via.map);
      PyList_SetItem(py_list, i, elem_py_dict);
      Py_DECREF(elem_py_dict);    
    } else {
      PyErr_SetString(PyExc_RuntimeError, "Unsuported type received");
      return NULL;
    }
  }
  return py_list;
}

static PyObject* python_dict_from_msgpack_map(msgpack_object_map map){
  PyObject* py_dict = PyDict_New();
  
  for (size_t i = 0; i < map.size; i++) {
    msgpack_object key = map.ptr[i].key;
    msgpack_object value = map.ptr[i].val;
    
    char *key_str = strndup(key.via.str.ptr, key.via.str.size);
    
    if (value.type == MSGPACK_OBJECT_BOOLEAN){
      PyDict_SetItemString(py_dict, key_str, PyBool_FromLong(value.via.boolean));
    } else if (value.type == MSGPACK_OBJECT_POSITIVE_INTEGER){
      PyDict_SetItemString(py_dict, key_str, PyLong_FromUnsignedLongLong(value.via.u64));
    } else if (value.type == MSGPACK_OBJECT_NEGATIVE_INTEGER){
      PyDict_SetItemString(py_dict, key_str, PyLong_FromLongLong(value.via.i64));
    } else if(value.type == MSGPACK_OBJECT_FLOAT32){
      PyDict_SetItemString(py_dict, key_str, PyFloat_FromDouble(value.via.f64));
    } else if(value.type == MSGPACK_OBJECT_FLOAT64){
      PyDict_SetItemString(py_dict, key_str, PyFloat_FromDouble(value.via.f64));
    } else if (value.type == MSGPACK_OBJECT_STR){
      char *val_str = strndup(value.via.str.ptr, value.via.str.size);
      PyDict_SetItemString(py_dict, key_str, PyUnicode_FromString(val_str));
      free(val_str);
    } else if (value.type == MSGPACK_OBJECT_ARRAY){
      PyObject* val_py_list = python_list_from_msgpack_array(value.via.array);
      PyDict_SetItemString(py_dict, key_str, val_py_list);
      Py_DECREF(val_py_list);    
    } else if (value.type == MSGPACK_OBJECT_MAP){
      PyObject* val_py_dict = python_dict_from_msgpack_map(value.via.map);
      PyDict_SetItemString(py_dict, key_str, val_py_dict);
      Py_DECREF(val_py_dict);    
    } else {
      PyErr_SetString(PyExc_RuntimeError, "Unsuported type received");
      return NULL;
    }
    free(key_str);
  }
  return py_dict;
}



static PyObject* server_recv(PyObject* self, PyObject* args) {
  int connfd, n_bytes, obs_width, obs_height, n_read, n_channels;
  double reward;
  char *buff;

  if (!PyArg_ParseTuple(args, "iiiii", &connfd, &n_bytes, &obs_width, &obs_height, &n_channels)) {
    PyErr_SetString(PyExc_TypeError,
                    "Arguments must be 5 integers: connection's fd, num. of bytes to read, obs. width and height, and num. channels.");
    return NULL;
  }

  // Create the buffer where the received image+data will be stored
  buff = (char*)malloc(n_bytes);
  if (buff == NULL) {
    PyErr_SetString(PyExc_Exception, "Failed to allocate memory for recv buffer");
    return NULL;
  }

  n_read = read_large_from_socket(connfd, buff, n_bytes);

  if (n_read < 0) {
    PyErr_SetString(PyExc_ConnectionError, "Failed to receive from MT, error reading from socket.");
    return NULL;
  } else if (n_read == 0) {
    close(connfd);
    PyErr_SetString(PyExc_ConnectionError, "Failed to receive from MT. Connection closed by peer: is MT down?");
    return NULL;
  }

  // Retreive size of the info buffer(last 4 bytes) the termination flag (1 bute) and reward (8 bytes)
  int n_bytes_info;
  memcpy(&n_bytes_info, &buff[n_bytes-4], 4);

  int termination = (int) buff[n_bytes-5];
  PyObject* py_termination = PyBool_FromLong(termination);

  memcpy(&reward, &buff[n_bytes-13], sizeof(reward));
  PyObject* py_reward = PyFloat_FromDouble(reward);

  PyObject* py_info = 0;

  if (n_bytes_info > 0){

    // Info will be sent 
    // Create the buffer where the received info will be stored

    unsigned char *info_buff = (unsigned char*)malloc(n_bytes_info);
    if (info_buff == NULL) {
      PyErr_SetString(PyExc_Exception, "Failed to allocate memory for recv information buffer");
      return NULL;
    }

    // Receive the info buffer
    n_read = read_large_from_socket(connfd, info_buff, n_bytes_info);

    if (n_read < 0) {
      PyErr_SetString(PyExc_ConnectionError, "Failed to receive info from MT, error reading from socket.");
      return NULL;
    } else if (n_read == 0) {
      close(connfd);
      PyErr_SetString(PyExc_ConnectionError, "Failed to receive info from MT. Connection closed by peer: is MT down?");
      return NULL;
    }

    // deserialize the information buffer and crate a python dictionary
    msgpack_unpacked info;
    msgpack_unpacked_init(&info);

    if (msgpack_unpack_next(&info, info_buff, n_bytes_info, NULL)) {
      msgpack_object obj = info.data;

      if (obj.type == MSGPACK_OBJECT_MAP) {
        msgpack_object_map map = obj.via.map;

        py_info = python_dict_from_msgpack_map(map);

      } else {
        PyErr_SetString(PyExc_RuntimeError, "Expected a map but got a different type");
        msgpack_unpacked_destroy(&info);
        free(info_buff);
        return NULL;
      }
    } else {
      PyErr_SetString(PyExc_RuntimeError, "Failed to unpack data");
      msgpack_unpacked_destroy(&info);
      free(info_buff);
      return NULL;
    }

    msgpack_unpacked_destroy(&info);
    free(info_buff);



  } else {
    // No info will be sent 
    // Info is just empty dict
    py_info = PyDict_New();
  }

  // Create the numpy array of the image
  npy_intp dims[3] = {obs_height, obs_width, n_channels};
  PyObject* array = PyArray_SimpleNewFromData(3, dims, NPY_UINT8, buff);
  if (!array) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to create NumPy array");
    return NULL;
  }

  // Make the NumPy array own its data.
  // This makes sure that NumPy handles the data lifecycle properly.
  PyArray_ENABLEFLAGS((PyArrayObject*)array, NPY_ARRAY_OWNDATA);

  PyObject* tuple = PyTuple_Pack(4, array, py_reward, py_termination, py_info);

  // Decreases the reference count of Python objects. Useful if the
  // objects' lifetime is no longer needed after creating the tuple.
  Py_DECREF(array);
  Py_DECREF(py_reward);
  Py_DECREF(py_termination);
  Py_DECREF(py_info);

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
