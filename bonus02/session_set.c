#include "session_set.h"

void session_set_init(session_set *p_sess_set, int *p_err) {
    p_sess_set->p_array = malloc(MAX_CLIENTS * sizeof(session));
    if (p_sess_set->p_array == NULL) {
        *p_err = true;
        return;
    }

    p_sess_set->elem_size = sizeof(session);
    p_sess_set->top = -1;
    p_sess_set->size = MAX_CLIENTS;
}

void session_set_add(session_set *p_sess_set, session *p_session, int *p_err) {
    int offset;

    // sanity check
    if (p_sess_set == NULL || p_sess_set->p_array == NULL) {
        *p_err = true;
        errno = EFAULT;
        return;
    }
    if (p_sess_set->top == p_sess_set->size - 1) {
        *p_err = true;
        errno = ENOSPC;
        return;
    }

    p_sess_set->top++;
    offset = p_sess_set->top * p_sess_set->elem_size;
    memcpy((char *)p_sess_set->p_array + offset, p_session, p_sess_set->elem_size);
}

bool session_set_contains(session_set *p_sess_set, int fd, int *p_err) {
    int i;
    int offset;
    session *p_session;

    // sanity check
    if (p_sess_set == NULL || p_sess_set->p_array == NULL) {
        *p_err = true;
        errno = EFAULT;
        return false;
    }

    for (i = 0; i <= p_sess_set->top; i++) {
        offset = i * p_sess_set->elem_size;
        p_session = (session *)((char *)p_sess_set->p_array + offset);
        if (p_session->fd_sock == fd) {
            return true;
        }
    }

    return false;
}

session *session_set_peek(session_set *p_sess_set, int fd, int *p_err) {
    int i;
    int offset;
    session *p_session;

    // sanity check
    if (p_sess_set == NULL || p_sess_set->p_array == NULL) {
        *p_err = true;
        errno = EFAULT;
        return NULL;
    }

    for (i = 0; i <= p_sess_set->top; i++) {
        offset = i * p_sess_set->elem_size;
        p_session = (session *)((char *)p_sess_set->p_array + offset);
        if (p_session->fd_sock == fd) {
            return p_session;
        }
    }

    return NULL;
}

void session_set_remove(session_set *p_sess_set, int fd, int *p_err) {
    int i;
    int offset;
    int offset_found = -1;
    int offset_last;
    session *p_session;

    // sanity check
    if (p_sess_set == NULL || p_sess_set->p_array == NULL) {
        *p_err = true;
        errno = EFAULT;
        return;
    }

    for (i = 0; i <= p_sess_set->top; i++) {
        offset = i * p_sess_set->elem_size;
        p_session = (session *)((char *)p_sess_set->p_array + offset);
        if (p_session->fd_sock == fd) {
            offset_found = offset;
            break;
        }
    }
    if (offset_found == -1) {
        return;
    }

    offset_last = p_sess_set->top * p_sess_set->elem_size;
    if (offset_found != offset_last) {
        memcpy((char *)p_sess_set->p_array + offset_found, (char *)p_sess_set->p_array + offset_last, p_sess_set->elem_size);
    }
    p_sess_set->top--;
}

void session_set_free(session_set *p_sess_set, int *p_err) {
    if (p_sess_set == NULL || p_sess_set->p_array == NULL) {
        *p_err = true;
        errno = EFAULT;
        return;
    }

    free(p_sess_set->p_array);
    p_sess_set->p_array = NULL;
    p_sess_set->top = -1;
    p_sess_set->size = 0;
}
