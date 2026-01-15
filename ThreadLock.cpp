#include "ThreadLock.h"

void ThreadLock::lock_read() {
    rw_mutex.lock_shared();
}

void ThreadLock::unlock_read() {
    rw_mutex.unlock_shared();
}

void ThreadLock::lock_write() {
    rw_mutex.lock();
}

void ThreadLock::unlock_write() {
    rw_mutex.unlock();
}