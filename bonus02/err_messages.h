#ifndef __ERR_MESSAGES_H
#define __ERR_MESSAGES_H

#include <stdio.h>
#include <errno.h>

#define MASTER_SO_NULL 1
#define CLIENT_SO_NULL 2

/**
 * @brief Prints socket set up error.
 */
void print_socket_set_up_error();

/**
 * @brief Prints bind error message.
 */
void print_bind_error_message();

/**
 * @brief Prints listen error message.
 */
void print_read_error_message();

/**
 * @brief Prints select error message.
 */
void print_listen_error_message();

/**
 * @brief Prints accept error message.
 */
void print_select_error_message();

/**
 * @brief Prints read error message.
 */
void print_accept_error_message();

#endif