#include "ProcessLock.h"
#ifdef _WIN32
    #include <windows.h>
#else
    #include <fcntl.h>
    #include <unistd.h>
#endif

ProcessLock::ProcessLock(const std::string& fileName) : path(fileName) {
#ifdef _WIN32
    handle = CreateFileA(path.c_str(), GENERIC_READ | GENERIC_WRITE,
                         FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                         OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
#else
    fd = open(path.c_str(), O_RDWR | O_CREAT, 0666);
#endif
}

ProcessLock::~ProcessLock() {
#ifdef _WIN32
    CloseHandle((HANDLE)handle);
#else
    close(fd);
#endif
}

void ProcessLock::lock_read() {
#ifdef _WIN32
    OVERLAPPED ov = {0};
    LockFileEx((HANDLE)handle, 0, 0, MAXDWORD, MAXDWORD, &ov);
#else
    struct flock fl = {F_RDLCK, SEEK_SET, 0, 0};
    fcntl(fd, F_SETLKW, &fl);
#endif
}

void ProcessLock::lock_write() {
#ifdef _WIN32
    OVERLAPPED ov = {0};
    LockFileEx((HANDLE)handle, LOCKFILE_EXCLUSIVE_LOCK, 0, MAXDWORD, MAXDWORD, &ov);
#else
    struct flock fl = {F_WRLCK, SEEK_SET, 0, 0};
    fcntl(fd, F_SETLKW, &fl);
#endif
}

void ProcessLock::unlock() {
#ifdef _WIN32
    OVERLAPPED ov = {0};
    UnlockFileEx((HANDLE)handle, 0, MAXDWORD, MAXDWORD, &ov);
#else
    struct flock fl = {F_UNLCK, SEEK_SET, 0, 0};
    fcntl(fd, F_SETLKW, &fl);
#endif
}