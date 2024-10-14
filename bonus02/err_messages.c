#include "err_messages.h"

void print_socket_set_up_error() {
    fprintf(stderr, "Error occurred while setting up the socket:\n\t");
    switch (errno) {
        case MASTER_SO_NULL:
            fprintf(stderr, "Master socket is not set.\n");
            break;
        case CLIENT_SO_NULL:
            fprintf(stderr, "Pointer to the client socket array is not set.\n");
            break;
        case EBADF:
            fprintf(stderr, "The argument sockfd is not a valid descriptor.\n");
            break;
        case EFAULT:
            fprintf(stderr, "The address pointed to by optval is not in a valid part of the process address space.\n");
            break;
        case EINVAL:
            fprintf(stderr, "optlen invalid in setsockopt().\n");
            break;
        case ENOPROTOOPT:
            fprintf(stderr, "The option is unknown at the level indicated.\n");
            break;
        case ENOTSOCK:
            fprintf(stderr, "The argument sockfd is a file, not a socket.\n");
            break;
        case EOPNOTSUPP:
            fprintf(stderr, "The socket is not of a type that supports the option.\n");
            break;
        default:
            fprintf(stderr, "Unknown error.\n");
            break;
    }
}

void print_bind_error_message() {
    fprintf(stderr, "Error occurred while binding the socket:\n\t");
    switch (errno) {
        case EACCES:
            fprintf(stderr, "The address is protected, and the user is not the superuser.\n");
            break;
        case EADDRINUSE:
            fprintf(stderr, "The given address is already in use.\n");
            break;
        case EBADF:
            fprintf(stderr, "The socket is not a valid file descriptor.\n");
            break;
        case EINVAL:
            fprintf(stderr, "The socket is already bound to an address.\n");
            break;
        case ENOTSOCK:
            fprintf(stderr, "The socket is not a socket.\n");
            break;
        case EADDRNOTAVAIL:
            fprintf(stderr, "The specified address is not available on this machine.\n");
            break;
        case EFAULT:
            fprintf(stderr, "The address points outside the user's accessible address space.\n");
            break;
        case ELOOP:
            fprintf(stderr, "Too many symbolic links were encountered in resolving the address.\n");
            break;
        case ENAMETOOLONG:
            fprintf(stderr, "The pathname of a socket address is too long.\n");
            break;
        case ENOENT:
            fprintf(stderr, "The file does not exist.\n");
            break;
        case ENOMEM:
            fprintf(stderr, "Insufficient memory is available.\n");
            break;
        case ENOTDIR:
            fprintf(stderr, "A component of the path prefix is not a directory.\n");
            break;
        case EROFS:
            fprintf(stderr, "The socket inode would reside on a read-only file system.\n");
            break;
        default:
            fprintf(stderr, "Unknown error.\n");
            break;
    }
}

void print_listen_error_message() {
    fprintf(stderr, "Error occurred while listening on the socket:\n\t");
    switch (errno) {
        case EADDRINUSE:
            fprintf(stderr, "Another socket is already listening on the same port.\n");
            break;
        case EBADF:
            fprintf(stderr, "The socket is not a valid file descriptor.\n");
            break;
        case ENOTSOCK:
            fprintf(stderr, "The socket is not a socket.\n");
            break;
        case EOPNOTSUPP:
            fprintf(stderr, "The socket is not of a type that supports the listen() operation.\n");
            break;
        default:
            fprintf(stderr, "Unknown error.\n");
            break;
    }
}

void print_select_error_message() {
    fprintf(stderr, "Error occurred while running select():\n\t");
    switch (errno) {
        case EBADF:
            fprintf(stderr, "An invalid file descriptor was given in one of the sets.\n");
            break;
        case EINTR:
            fprintf(stderr, "A signal was caught.\n");
            break;
        case EINVAL:
            fprintf(stderr, "nfds is negative or the value contained within timeout is invalid.\n");
            break;
        case ENOMEM:
            fprintf(stderr, "Unable to allocate memory for internal tables.\n");
            break;
        default:
            fprintf(stderr, "Unknown error.\n");
            break;
    }
}

void print_accept_error_message() {
    fprintf(stderr, "Error occurred while accepting the socket:\n\t");
    switch (errno) {
        case EBADF:
            fprintf(stderr, "The socket is not a valid file descriptor.\n");
            break;
        case ECONNABORTED:
            fprintf(stderr, "A connection has been aborted.\n");
            break;
        case EFAULT:
            fprintf(stderr, "The address points outside the user's accessible address space.\n");
            break;
        case EINTR:
            fprintf(stderr, "A signal was caught.\n");
            break;
        case EINVAL:
            fprintf(stderr, "The socket is not listening for connections.\n");
            break;
        case EMFILE:
            fprintf(stderr, "The per-process limit on the number of open file descriptors has been reached.\n");
            break;
        case ENFILE:
            fprintf(stderr, "The system-wide limit on the total number of open files has been reached.\n");
            break;
        case ENOBUFS:
            fprintf(stderr, "Not enough free memory for the operation.\n");
            break;
        case ENOMEM:
            fprintf(stderr, "Not enough memory for the operation.\n");
            break;
        case ENOTSOCK:
            fprintf(stderr, "The socket is not a socket.\n");
            break;
        case EOPNOTSUPP:
            fprintf(stderr, "The socket is not of a type that supports the accept() operation.\n");
            break;
        case EPROTO:
            fprintf(stderr, "Protocol error.\n");
            break;
        case EWOULDBLOCK:
            fprintf(stderr, "The socket is marked non-blocking and no connections are present to be accepted.\n");
            break;
        default:
            fprintf(stderr, "Unknown error.\n");
            break;
    }
}

void print_read_error_message() {
    fprintf(stderr, "Error occurred while reading from the socket:\n\t");
    switch (errno) {
        case EBADF:
            fprintf(stderr, "The socket is not a valid file descriptor.\n");
            break;
        case EFAULT:
            fprintf(stderr, "The buffer is outside the process's address space.\n");
            break;
        case EINTR:
            fprintf(stderr, "The call was interrupted by a signal before any data was read.\n");
            break;
        case EINVAL:
            fprintf(stderr, "The socket is not bound to an address and the protocol does not support listening on an unbound socket.\n");
            break;
        case EIO:
            fprintf(stderr, "An I/O error occurred.\n");
            break;
        case EISDIR:
            fprintf(stderr, "The file descriptor refers to a directory.\n");
            break;
        case EMSGSIZE:
            fprintf(stderr, "The message is too large to be sent all at once, as the socket requires.\n");
            break;
        case ENOBUFS:
            fprintf(stderr, "The output queue for a network interface was full.\n");
            break;
        case ENOMEM:
            fprintf(stderr, "Insufficient memory is available.\n");
            break;
        case ENOTCONN:
            fprintf(stderr, "The socket is associated with a connection-oriented protocol and has not been connected.\n");
            break;
        case ENOTSOCK:
            fprintf(stderr, "The socket argument does not refer to a socket.\n");
            break;
        case EOPNOTSUPP:
            fprintf(stderr, "The socket is not of a type that supports the operation.\n");
            break;
        case ETIMEDOUT:
            fprintf(stderr, "The connection timed out during connection establishment, or due to a transmission timeout on active connection.\n");
            break;
        default:
            fprintf(stderr, "Unknown error.\n");
            break;
    }
}