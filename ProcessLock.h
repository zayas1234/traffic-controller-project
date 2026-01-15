#ifndef PROCESSLOCK_H
#define PROCESSLOCK_H

#include <string>

class ProcessLock {
private:
    std::string path;
#ifdef _WIN32
    void* handle;
#else
    int fd;
#endif

public:
    ProcessLock(const std::string& fileName);
    ~ProcessLock();
    void lock_read();
    void lock_write();
    void unlock();
};

#endif