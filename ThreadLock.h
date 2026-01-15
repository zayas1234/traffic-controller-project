#ifndef THREADLOCK_H
#define THREADLOCK_H

#include <shared_mutex>
#include <string>

class ThreadLock {
private:
    std::shared_mutex rw_mutex;
public:
    void lock_read();    // Múltiples lectores
    void lock_write();   // Escritor único
    void unlock_read();
    void unlock_write();
};

#endif