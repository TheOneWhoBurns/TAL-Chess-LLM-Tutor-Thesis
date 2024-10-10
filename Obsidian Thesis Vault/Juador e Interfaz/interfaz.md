![[Screenshot 2024-09-24 at 9.51.12 AM.png]]
Arquitectura del sistema:
1. Interfaz de [[Jugador]]: Una interfaz basada en web para que los jugadores interactúen con el tablero de ajedrez y reciban comentarios del [[BOT - Virtual GM]].
2. Backend de [[Django]]: Maneja las solicitudes/respuestas HTTP y orquesta el flujo entre los componentes.
3. [[Módulo de lógica de ajedrez:]] Administra el estado del juego, la validación de movimientos y coordina entre el  Motor de Ajedrez y el LLM.
4. [[Motor de ajedrez]] Maia: Proporciona análisis del tablero y sugerencias de movimientos.
5. [[Interfaz del LLM]]: Prepara los mensajes para el [[LLM]] en función del estado del juego y el análisis del motor.
6. [[Modelo de lenguaje]]: Genera explicaciones y consejos en lenguaje humano.

![[Pasted image 20240924103235.png]]
![[Pasted image 20240924111002.png]]