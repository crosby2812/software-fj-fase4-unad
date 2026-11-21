# Sistema Integral de Gestión de Clientes, Servicios y Reservas — Software FJ (Fase 4)

Proyecto desarrollado para el curso **Programación (código 213023)**, programa de **Ingeniería de Sistemas (ECBTI)** de la **Universidad Nacional Abierta y a Distancia (UNAD)**[cite: 1, 2, 6].

## Descripción general
Aplicación orientada a objetos en Python **sin uso de bases de datos** para **Software FJ**[cite: 6]. Gestiona clientes, servicios (`ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`) y reservas mediante objetos, listas en memoria y registro de eventos y errores en el archivo de logs `software_fj.log`[cite: 6, 7, 8].

## Arquitectura POO y manejo de excepciones
- **Clases abstractas:** `EntidadSistema` (entidades generales del sistema) y `Servicio` (contrato base con métodos abstractos y sobrecarga lógica de `calcular_costo` con parámetros opcionales de impuesto y descuento)[cite: 7].
- **Encapsulación y validaciones:** `Cliente` valida nombre, correo y documento mediante propiedades y setters[cite: 7].
- **Polimorfismo:** `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` sobrescriben `validar_parametros`, `_calcular_subtotal` y `describir`[cite: 7].
- **Ciclo de vida de reservas:** `Reserva` y `GestorSoftwareFJ` controlan estados (`PENDIENTE`, `CONFIRMADA`, `PROCESADA`, `CANCELADA`) y reglas de negocio[cite: 7].
- **Excepciones y logs:** Incluye excepciones personalizadas (`DatoInvalidoError`, `ParametroFaltanteError`, `OperacionNoPermitidaError`, `ServicioNoDisponibleError`, `CalculoInconsistenteError`, `ReservaError`), bloques `try/except/else/finally`, encadenamiento (`raise ... from exc`) y registro continuo en `software_fj.log`[cite: 7, 8].

## Ejecución
Desde la carpeta del proyecto en terminal/PowerShell:

```bash
python main.py