#include "ProcessLock.h" // Cambiado para que coincida con el archivo de procesos
#include <iostream>
#include <thread>
#include <vector>

// Usamos ProcessLock en lugar de un nombre genérico
void tareaLector(int id, ProcessLock& lock) {
    std::cout << "[Lector " << id << "] Esperando turno..." << std::endl;
    lock.lock_read();
    
    std::cout << "[Lector " << id << "] >>> LEYENDO el archivo." << std::endl;
    // Durante estos 3 segundos, otros lectores pueden entrar, pero los escritores no
    std::this_thread::sleep_for(std::chrono::seconds(3)); 
    
    lock.unlock();
    std::cout << "[Lector " << id << "] Libero el archivo." << std::endl;
}

void tareaEscritor(int id, ProcessLock& lock) {
    std::cout << "[Escritor " << id << "] !!! Intentando acceso exclusivo..." << std::endl;
    lock.lock_write();
    
    std::cout << "[Escritor " << id << "] === ESCRIBIENDO en el archivo." << std::endl;
    // Durante estos 5 segundos, NADIE mas puede entrar
    std::this_thread::sleep_for(std::chrono::seconds(5)); 
    
    lock.unlock();
    std::cout << "[Escritor " << id << "] Libero el archivo (Escritura terminada)." << std::endl;
}

int main() {
    // Creamos la instancia de la clase de procesos
    ProcessLock miBloqueo("datos.txt");
    int opcion;

    std::cout << "--- Sistema de Bloqueo de Archivos (Procesos e Hilos) ---" << std::endl;
    std::cout << "1. Probar con Hilos (Simultaneos)" << std::endl;
    std::cout << "2. Probar entre Procesos (Abrir otra terminal)" << std::endl;
    std::cout << "Seleccione: ";
    std::cin >> opcion;

    if (opcion == 1) {
        // Probamos concurrencia de hilos dentro de este mismo proceso
        std::thread t1(tareaLector, 1, std::ref(miBloqueo));
        std::thread t2(tareaLector, 2, std::ref(miBloqueo));
        std::thread t3(tareaEscritor, 3, std::ref(miBloqueo));
        std::thread t4(tareaLector, 4, std::ref(miBloqueo));

        t1.join(); t2.join(); t3.join(); t4.join();
    } 
    else {
        // Probamos bloqueo para otros programas externos
        std::cout << "Bloqueando archivo para escritura..." << std::endl;
        miBloqueo.lock_write();
        std::cout << "ARCHIVO BLOQUEADO POR ESTA TERMINAL." << std::endl;
        std::cout << "Intenta ejecutar este programa en OTRA terminal ahora mismo." << std::endl;
        std::cout << "Presiona ENTER para liberar y salir." << std::endl;
        
        std::cin.ignore();
        std::cin.get();
        miBloqueo.unlock();
    }

    return 0;
}