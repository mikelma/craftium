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
#include <stdint.h>

#define SA struct sockaddr

// Recursive function to print elements of an arbitrary-dimensional array
void print_array_recursive(uint8_t* data, npy_intp* shape, npy_intp* strides, int ndim, int dim_index, npy_intp* indices) {
    if (dim_index == ndim - 1) {
        // Base case: print the elements in the last dimension
        printf("[");
        for (npy_intp i = 0; i < shape[dim_index]; ++i) {
            indices[dim_index] = i;

            // Compute the flat index based on strides and indices
            npy_intp flat_index = 0;
            for (int j = 0; j < ndim; ++j) {
                flat_index += indices[j] * strides[j] / sizeof(uint8_t);
            }

            printf("%u", data[flat_index]);
            if (i < shape[dim_index] - 1) {
                printf(", ");
            }
        }
        printf("]");
    } else {
        // Recursive case: iterate through the current dimension
        printf("[");
        for (npy_intp i = 0; i < shape[dim_index]; ++i) {
            indices[dim_index] = i;
            print_array_recursive(data, shape, strides, ndim, dim_index + 1, indices);
            if (i < shape[dim_index] - 1) {
                printf(", ");
            }
        }
        printf("]");
    }
}

// Wrapper function
void print_array(PyObject* array) {
    PyArrayObject* np_array = (PyArrayObject*)array;

    // Get the data buffer, shape, and strides
    uint8_t* data = (uint8_t*)PyArray_DATA(np_array);
    npy_intp* shape = PyArray_DIMS(np_array);
    npy_intp* strides = PyArray_STRIDES(np_array);
    int ndim = PyArray_NDIM(np_array);

    // Allocate an indices array for recursive traversal
    npy_intp* indices = (npy_intp*)calloc(ndim, sizeof(npy_intp));
    if (!indices) {
        fprintf(stderr, "Failed to allocate memory for indices.\n");
        return;
    }

    // Start the recursive print
    print_array_recursive(data, shape, strides, ndim, 0, indices);
    printf("\n");

    // Free allocated memory
    free(indices);
}

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

static PyObject* server_recv(PyObject* self, PyObject* args) {
  int connfd, n_bytes, obs_width, obs_height, n_read, n_channels, n_vox_channels, voxel_x, voxel_y, voxel_z;
  float dtime;
  double reward;
  int32_t yaw, pitch;
  char *buff;

  if (!PyArg_ParseTuple(args, "iiiiiiiii", &connfd, &n_bytes, &obs_width, &obs_height, &n_channels, &n_vox_channels, &voxel_x, &voxel_y, &voxel_z)) {
    PyErr_SetString(PyExc_TypeError,
                    "Arguments must be 9 integers: connection's fd, num. of bytes to read, obs. width and height, num. channels, num. vox channels, voxel_obs x,y and z dims.");
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
    free(buff);
    PyErr_SetString(PyExc_ConnectionError, "Failed to receive from MT, error reading from socket.");
    return NULL;
  } else if (n_read == 0) {
    free(buff);
    close(connfd);
    PyErr_SetString(PyExc_ConnectionError, "Failed to receive from MT. Connection closed by peer: is MT down?");
    return NULL;
  }

  // Retrieve the termination flag and reward
  int termination = (int) buff[n_bytes-1];
  PyObject* py_termination = PyBool_FromLong(termination);

  memcpy(&reward, &buff[n_bytes-9], sizeof(reward));
  PyObject* py_reward = PyFloat_FromDouble(reward);

  // Retrieve the delta time
  memcpy(&dtime, &buff[n_bytes-13], sizeof(dtime));
  PyObject* py_dtime = PyFloat_FromDouble((double)dtime);

  // Retrieve backwards the yaw [4], pitch [4], velocity [12] and position [12] = 32 bytes
  float* array_pos_data = (float*)malloc(3 * sizeof(float));
  float* array_vel_data = (float*)malloc(3 * sizeof(float));
  memcpy(&yaw, &buff[n_bytes-17], sizeof(int32_t));
  memcpy(&pitch, &buff[n_bytes-21], sizeof(int32_t));
  memcpy(array_vel_data, &buff[n_bytes-33], 3 * sizeof(float));
  memcpy(array_pos_data, &buff[n_bytes-45], 3 * sizeof(float));
  npy_intp dims_v3f[1] = {3};
  PyObject* pyarray_pos = PyArray_SimpleNewFromData(1, dims_v3f, NPY_FLOAT32, array_pos_data);
  PyObject* pyarray_vel = PyArray_SimpleNewFromData(1, dims_v3f, NPY_FLOAT32, array_vel_data);
  PyObject* py_pitch = PyLong_FromSsize_t(pitch);
  PyObject* py_yaw = PyLong_FromSsize_t(yaw);

  // Create separate memory allocations for the RGB and voxel data
  char* array_rgb_data = (char*)malloc(obs_height * obs_width * n_channels);
  uint32_t* array_vox_data = (uint32_t*)malloc(voxel_x * voxel_y * voxel_z * n_vox_channels * sizeof(uint32_t));

  if (!array_rgb_data || !array_vox_data) {
    free(buff);
    free(array_rgb_data);
    free(array_vox_data);
    free(array_pos_data);
    free(array_vel_data);
    Py_XDECREF(py_termination);
    Py_XDECREF(py_reward);
    Py_XDECREF(py_dtime);
    Py_XDECREF(pyarray_pos);
    Py_XDECREF(pyarray_vel);
    Py_XDECREF(py_pitch);
    Py_XDECREF(py_yaw);
    PyErr_SetString(PyExc_Exception, "Failed to allocate memory for array data");
    return NULL;
  }

  // Copy the RGB data
  memcpy(array_rgb_data, buff, obs_height * obs_width * n_channels);
  // Copy the voxel data, converting from bytes to uint32_t
  memcpy(array_vox_data, buff + obs_height * obs_width * n_channels,
         voxel_x * voxel_y * voxel_z * n_vox_channels * sizeof(uint32_t));

  // Free the original buffer as we no longer need it
  free(buff);

  // Create the numpy arrays with their own separate memory
  npy_intp dims[3] = {obs_height, obs_width, n_channels};
  PyObject* pyarray_rgb = PyArray_SimpleNewFromData(3, dims, NPY_UINT8, array_rgb_data);

  npy_intp dims_vox[4] = {voxel_z, voxel_y, voxel_x, n_vox_channels};
  PyObject* pyarray_vox = PyArray_SimpleNewFromData(4, dims_vox, NPY_UINT32, array_vox_data);

  if (!pyarray_rgb || !pyarray_vox) {
    free(array_rgb_data);
    free(array_vox_data);
    Py_XDECREF(pyarray_rgb);
    Py_XDECREF(pyarray_vox);
    Py_XDECREF(py_termination);
    Py_XDECREF(py_reward);
    Py_XDECREF(py_dtime);
    Py_XDECREF(pyarray_pos);
    Py_XDECREF(pyarray_vel);
    Py_XDECREF(py_pitch);
    Py_XDECREF(py_yaw);
    PyErr_SetString(PyExc_RuntimeError, "Failed to create NumPy array");
    return NULL;
  }

  // Now it's safe to enable OWNDATA as each array has its own allocation
  PyArray_ENABLEFLAGS((PyArrayObject*)pyarray_pos, NPY_ARRAY_OWNDATA);
  PyArray_ENABLEFLAGS((PyArrayObject*)pyarray_vel, NPY_ARRAY_OWNDATA);
  PyArray_ENABLEFLAGS((PyArrayObject*)pyarray_rgb, NPY_ARRAY_OWNDATA);
  PyArray_ENABLEFLAGS((PyArrayObject*)pyarray_vox, NPY_ARRAY_OWNDATA);

  PyObject* tuple = PyTuple_Pack(9, pyarray_rgb, pyarray_vox, pyarray_pos, pyarray_vel, py_pitch, py_yaw, py_dtime, py_reward, py_termination);

  // Safe to DECREF everything as tuple has increased their reference counts
  Py_DECREF(py_reward);
  Py_DECREF(py_dtime);
  Py_DECREF(py_termination);
  Py_DECREF(pyarray_pos);
  Py_DECREF(pyarray_vel);
  Py_DECREF(py_pitch);
  Py_DECREF(py_yaw);
  Py_DECREF(pyarray_rgb);
  Py_DECREF(pyarray_vox);

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
