from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import logging
from typing import overload
import uuid


# ==============================================================================
# 1. CONFIGURACIÓN DE LOGS (SIN BASE DE DATOS)
# ==============================================================================
def configurar_logger(archivo_log: str = "software_fj.log") -> logging.Logger:
    """Configura y devuelve un logger que guarda eventos y errores en archivo."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(archivo_log, mode="a", encoding="utf-8")
        file_handler.setFormatter(formato)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formato)
        logger.addHandler(stream_handler)

    return logger


logger = configurar_logger()


# ==============================================================================
# 2. EXCEPCIONES PERSONALIZADAS DEL DOMINIO
# ==============================================================================
class ErrorSoftwareFJ(Exception):
    """Excepción base para errores del sistema Software FJ."""


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato tiene formato o valor inválido."""


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando faltan parámetros obligatorios o están vacíos."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta una operación no válida por estado o regla."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio no está disponible para ser reservado."""


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando ocurre un error o inconsistencia en cálculos financieros."""


class ReservaError(ErrorSoftwareFJ):
    """Se lanza ante fallos al crear, confirmar, procesar o cancelar reservas."""


# ==============================================================================
# 3. CLASE ABSTRACTA GENERAL DEL SISTEMA
# ==============================================================================
class EntidadSistema(ABC):
    """Representa una entidad general dentro de Software FJ."""

    def __init__(self, id_entidad: str | None = None) -> None:
        if id_entidad is not None and not str(id_entidad).strip():
            raise ParametroFaltanteError("El ID de la entidad no puede estar vacío.")
        self._id: str = str(id_entidad).strip() if id_entidad else str(uuid.uuid4())[:8]
        self._fecha_creacion: datetime = datetime.now()

    @property
    def id(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        """Retorna la fecha y hora de creación de la entidad."""
        return self._fecha_creacion

    @abstractmethod
    def resumen(self) -> str:
        """Retorna una descripción resumida de la entidad."""


# ==============================================================================
# 4. CLASE CLIENTE (ENCAPSULACIÓN Y VALIDACIONES ESTRICTAS)
# ==============================================================================
class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con encapsulación y validaciones."""

    def __init__(
        self,
        nombre: str,
        correo: str,
        documento: str,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(id_entidad)
        self.nombre = nombre
        self.correo = correo
        self.documento = documento

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        if len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        correo_limpio = valor.strip()
        if "@" not in correo_limpio or "." not in correo_limpio.split("@")[-1]:
            raise DatoInvalidoError(f"Correo electrónico inválido: '{correo_limpio}'.")
        self._correo = correo_limpio.lower()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El documento de identidad es obligatorio.")
        doc_limpio = valor.strip()
        if not doc_limpio.isalnum() or len(doc_limpio) < 5:
            raise DatoInvalidoError(
                f"Documento inválido ('{doc_limpio}'): debe ser alfanumérico y tener mínimo 5 caracteres."
            )
        self._documento = doc_limpio

    def resumen(self) -> str:
        return f"Cliente[{self.id}] {self.nombre} | Doc: {self.documento} | Email: {self.correo}"


# ==============================================================================
# 5. CLASE ABSTRACTA SERVICIO Y SUBCLASES ESPECIALIZADAS (POLIMORFISMO)
# ==============================================================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(id_entidad)
        if not isinstance(nombre, str) or not nombre.strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        self._nombre: str = nombre.strip()
        self._tarifa_base: float = self._validar_tarifa(tarifa_base)
        self._disponible: bool = bool(disponible)

    @staticmethod
    def _validar_tarifa(tarifa: float) -> float:
        """Valida que la tarifa base sea numérica y positiva."""
        try:
            valor = float(tarifa)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError("La tarifa base debe ser un valor numérico.") from exc

        if valor <= 0:
            raise DatoInvalidoError("La tarifa base debe ser mayor que cero.")
        return valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, estado: bool) -> None:
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion: int | float) -> None:
        """Valida duración o parámetros propios del servicio."""

    @overload
    def calcular_costo(self, duracion: int | float) -> float: ...

    @overload
    def calcular_costo(self, duracion: int | float, impuesto: float) -> float: ...

    @overload
    def calcular_costo(
        self, duracion: int | float, impuesto: float, descuento: float
    ) -> float: ...

    def calcular_costo(
        self,
        duracion: int | float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
    ) -> float:
        """Calcula el costo con sobrecarga lógica mediante parámetros opcionales."""
        self.validar_parametros(duracion)
        try:
            dur = float(duracion)
            imp = float(impuesto)
            desc = float(descuento)
        except (TypeError, ValueError) as exc:
            raise CalculoInconsistenteError(
                "Duración, impuesto o descuento no son numéricos."
            ) from exc

        if imp < 0 or imp > 1:
            raise CalculoInconsistenteError("El impuesto debe estar entre 0.0 y 1.0 (ej. 0.19).")
        if desc < 0 or desc > 1:
            raise CalculoInconsistenteError("El descuento debe estar entre 0.0 y 1.0 (ej. 0.10).")

        subtotal = self._calcular_subtotal(dur)
        con_descuento = subtotal * (1 - desc)
        total = con_descuento * (1 + imp)

        if total < 0:
            raise CalculoInconsistenteError("El cálculo arrojó un total negativo.")
        return round(total, 2)

    @abstractmethod
    def _calcular_subtotal(self, duracion: float) -> float:
        """Calcula el subtotal específico de cada tipo de servicio."""

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción detallada del servicio."""

    def resumen(self) -> str:
        estado_txt = "Disponible" if self._disponible else "No disponible"
        return f"{self.describir()} | Estado: {estado_txt}"


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas (por horas)."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(nombre, tarifa_base, disponible, id_entidad)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad_personas = capacidad_personas

    def validar_parametros(self, duracion: int | float) -> None:
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool):
            raise DatoInvalidoError("La duración de la sala debe ser un número de horas.")
        if duracion < 1 or duracion > 12:
            raise DatoInvalidoError("La reserva de sala debe ser de entre 1 y 12 horas.")

    def _calcular_subtotal(self, duracion: float) -> float:
        return self.tarifa_base * duracion

    def describir(self) -> str:
        return (
            f"Sala '{self.nombre}' (Cap. {self.capacidad_personas} pax, "
            f"${self.tarifa_base:,.2f}/h)"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos (por días)."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: float,
        codigo_equipo: str,
        disponible: bool = True,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(nombre, tarifa_base, disponible, id_entidad)
        if not isinstance(codigo_equipo, str) or not codigo_equipo.strip():
            raise ParametroFaltanteError("El código del equipo es obligatorio.")
        self.codigo_equipo = codigo_equipo.strip().upper()

    def validar_parametros(self, duracion: int | float) -> None:
        if not isinstance(duracion, int) or isinstance(duracion, bool):
            raise DatoInvalidoError("El alquiler de equipo exige un número entero de días.")
        if duracion < 1 or duracion > 30:
            raise DatoInvalidoError("El alquiler de equipo debe ser de entre 1 y 30 días.")

    def _calcular_subtotal(self, duracion: float) -> float:
        return (self.tarifa_base * duracion) + 15000.0

    def describir(self) -> str:
        return (
            f"Equipo '{self.nombre}' [Cod: {self.codigo_equipo}] "
            f"(${self.tarifa_base:,.2f}/día + $15,000.00 logística)"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de asesoría técnica/arquitectura (por sesiones/horas)."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(nombre, tarifa_base, disponible, id_entidad)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ParametroFaltanteError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion: int | float) -> None:
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool):
            raise DatoInvalidoError("La duración de la asesoría debe ser numérica.")
        if duracion < 0.5 or duracion > 40:
            raise DatoInvalidoError("La asesoría debe durar entre 0.5 y 40 horas.")

    def _calcular_subtotal(self, duracion: float) -> float:
        return self.tarifa_base * duracion

    def describir(self) -> str:
        return (
            f"Asesoría '{self.nombre}' [{self.especialidad}] "
            f"(${self.tarifa_base:,.2f}/h)"
        )


# ==============================================================================
# 6. CLASE RESERVA Y GESTOR DEL SISTEMA (LISTAS EN MEMORIA + EXCEPCIONES)
# ==============================================================================
class EstadoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


class Reserva(EntidadSistema):
    """Integra cliente, servicio, duración, costo y ciclo de vida de reserva."""

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int | float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(id_entidad)
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Debe proporcionar una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe proporcionar una instancia válida de Servicio.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible actualmente."
            )

        try:
            self._costo_total: float = servicio.calcular_costo(
                duracion, impuesto=impuesto, descuento=descuento
            )
        except ErrorSoftwareFJ as exc:
            raise ReservaError(
                f"No fue posible calcular la reserva para '{cliente.nombre}'."
            ) from exc

        self.cliente: Cliente = cliente
        self.servicio: Servicio = servicio
        self.duracion: int | float = duracion
        self.estado: EstadoReserva = EstadoReserva.PENDIENTE

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def confirmar(self) -> None:
        if self.estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(
                f"La reserva {self.id} está CANCELADA y no puede confirmarse."
            )
        if self.estado in (EstadoReserva.CONFIRMADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"La reserva {self.id} ya se encuentra en estado {self.estado.value}."
            )
        self.estado = EstadoReserva.CONFIRMADA

    def procesar(self) -> None:
        if self.estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual: {self.estado.value}."
            )
        self.estado = EstadoReserva.PROCESADA

    def cancelar(self) -> None:
        if self.estado == EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError(
                f"No se puede cancelar la reserva {self.id} porque ya fue PROCESADA."
            )
        if self.estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(f"La reserva {self.id} ya está CANCELADA.")
        self.estado = EstadoReserva.CANCELADA

    def resumen(self) -> str:
        return (
            f"Reserva[{self.id}] | {self.cliente.nombre} -> {self.servicio.nombre} "
            f"| Duración: {self.duracion} | Total: ${self.costo_total:,.2f} "
            f"| Estado: {self.estado.value}"
        )


class GestorSoftwareFJ:
    """Coordina listas internas de clientes, servicios y reservas sin base de datos."""

    def __init__(self) -> None:
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, cliente: Cliente) -> None:
        if any(c.documento == cliente.documento for c in self.clientes):
            raise OperacionNoPermitidaError(
                f"Ya existe un cliente registrado con el documento {cliente.documento}."
            )
        self.clientes.append(cliente)

    def registrar_servicio(self, servicio: Servicio) -> None:
        if any(s.id == servicio.id for s in self.servicios):
            raise OperacionNoPermitidaError(
                f"Ya existe un servicio con el ID {servicio.id}."
            )
        self.servicios.append(servicio)

    def crear_reserva(
        self,
        documento_cliente: str,
        id_servicio: str,
        duracion: int | float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
    ) -> Reserva:
        cliente = next((c for c in self.clientes if c.documento == documento_cliente), None)
        if cliente is None:
            raise DatoInvalidoError(f"Cliente con documento '{documento_cliente}' no encontrado.")

        servicio = next((s for s in self.servicios if s.id == id_servicio), None)
        if servicio is None:
            raise DatoInvalidoError(f"Servicio con ID '{id_servicio}' no encontrado.")

        reserva = Reserva(
            cliente=cliente,
            servicio=servicio,
            duracion=duracion,
            impuesto=impuesto,
            descuento=descuento,
        )
        self.reservas.append(reserva)
        return reserva


# ==============================================================================
# 7. EJECUCIÓN DE 12 OPERACIONES SIMULADAS CON TRY/EXCEPT/ELSE/FINALLY
# ==============================================================================
def ejecutar_simulacion() -> None:
    """Ejecuta al menos 10 operaciones válidas e inválidas demostrando resiliencia."""
    gestor = GestorSoftwareFJ()
    logger.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ (FASE 4) ===")

    operaciones = [
        (
            "OP-01: Registrar cliente válido (Ana Gómez)",
            lambda: gestor.registrar_cliente(
                Cliente("Ana Gómez", "ana.gomez@empresa.co", "1090456123", "CLI-01")
            ),
        ),
        (
            "OP-02: Registrar cliente inválido (correo mal formado)",
            lambda: gestor.registrar_cliente(
                Cliente("Carlos Ruiz", "carlos_sin_arroba", "1090999888", "CLI-02")
            ),
        ),
        (
            "OP-03: Registrar segundo cliente válido (Laura Pérez)",
            lambda: gestor.registrar_cliente(
                Cliente("Laura Pérez", "laura.perez@tech.org", "1090777666", "CLI-03")
            ),
        ),
        (
            "OP-04: Crear servicio ReservaSala válido",
            lambda: gestor.registrar_servicio(
                ReservaSala("Sala Reuniones Norte", 80000.0, 12, True, "SRV-SALA1")
            ),
        ),
        (
            "OP-05: Crear servicio AlquilerEquipo válido",
            lambda: gestor.registrar_servicio(
                AlquilerEquipo("Laptop Workstation", 65000.0, "EQ-LAP-09", True, "SRV-EQ1")
            ),
        ),
        (
            "OP-06: Crear servicio AsesoriaEspecializada válido",
            lambda: gestor.registrar_servicio(
                AsesoriaEspecializada(
                    "Arquitectura Cloud & POO", 120000.0, "Software", True, "SRV-ASE1"
                )
            ),
        ),
        (
            "OP-07: Crear servicio inválido (tarifa negativa)",
            lambda: gestor.registrar_servicio(
                ReservaSala("Sala Auditorio", -50000.0, 30, True, "SRV-SALA2")
            ),
        ),
        (
            "OP-08: Crear, confirmar y procesar reserva exitosa de sala",
            lambda: _flujo_reserva_exitoso(
                gestor, "1090456123", "SRV-SALA1", 3, impuesto=0.19, descuento=0.10
            ),
        ),
        (
            "OP-09: Reserva fallida por duración inválida en alquiler de equipo",
            lambda: gestor.crear_reserva("1090777666", "SRV-EQ1", 2.5),
        ),
        (
            "OP-10: Crear y confirmar reserva exitosa de asesoría",
            lambda: _flujo_confirmar_reserva(gestor, "1090777666", "SRV-ASE1", 4),
        ),
        (
            "OP-11: Reserva fallida por servicio no disponible",
            lambda: _reserva_servicio_no_disponible(gestor, "1090456123", "SRV-EQ1"),
        ),
        (
            "OP-12: Operación no permitida (cancelar reserva ya procesada)",
            lambda: _cancelar_primera_reserva_procesada(gestor),
        ),
    ]

    for descripcion, accion in operaciones:
        try:
            resultado = accion()
        except ErrorSoftwareFJ as exc:
            try:
                raise OperacionNoPermitidaError(
                    f"Fallo controlado en '{descripcion}'"
                ) from exc
            except OperacionNoPermitidaError as error_encadenado:
                logger.error("%s | Causa: %s", error_encadenado, exc)
        except Exception as exc:
            logger.critical("Error inesperado en '%s': %s", descripcion, exc)
        else:
            detalle = resultado.resumen() if isinstance(resultado, EntidadSistema) else str(resultado)
            logger.info("OK -> %s | %s", descripcion, detalle)
        finally:
            logger.debug("Finalizó ciclo de operación: %s", descripcion)

    logger.info(
        "=== RESUMEN FINAL | Clientes: %d | Servicios: %d | Reservas: %d ===",
        len(gestor.clientes),
        len(gestor.servicios),
        len(gestor.reservas),
    )


def _flujo_reserva_exitoso(
    gestor: GestorSoftwareFJ,
    doc: str,
    srv_id: str,
    duracion: int | float,
    impuesto: float = 0.0,
    descuento: float = 0.0,
) -> Reserva:
    reserva = gestor.crear_reserva(doc, srv_id, duracion, impuesto, descuento)
    reserva.confirmar()
    reserva.procesar()
    return reserva


def _flujo_confirmar_reserva(
    gestor: GestorSoftwareFJ,
    doc: str,
    srv_id: str,
    duracion: int | float,
) -> Reserva:
    reserva = gestor.crear_reserva(doc, srv_id, duracion)
    reserva.confirmar()
    return reserva


def _reserva_servicio_no_disponible(
    gestor: GestorSoftwareFJ,
    doc: str,
    srv_id: str,
) -> Reserva:
    servicio = next(s for s in gestor.servicios if s.id == srv_id)
    servicio.cambiar_disponibilidad(False)
    try:
        return gestor.crear_reserva(doc, srv_id, 2)
    finally:
        servicio.cambiar_disponibilidad(True)


def _cancelar_primera_reserva_procesada(gestor: GestorSoftwareFJ) -> None:
    procesada = next(r for r in gestor.reservas if r.estado == EstadoReserva.PROCESADA)
    procesada.cancelar()


if __name__ == "__main__":
    ejecutar_simulacion()