## 36. El archivo de la humanidad

### La colección que no cabe

La propuesta llega al Archivo en seis cajas y un documento digital.

Un equipo de investigadoras quiere construir una máquina capaz de continuar texto. No busca archivar documentos para recuperarlos después mediante un índice. Quiere exponer un sistema matemático a enormes cantidades de lenguaje para que aprenda regularidades: qué signos suelen seguir a otros, qué relaciones persisten a través de una frase y qué formas adopta una respuesta cuando cambia la pregunta.

Necesitan libros, artículos, manuales, código, cartas, debates y conversaciones.

Necesitan más texto del que una persona podría leer en muchas vidas.

La dirección mira sus depósitos y ve una oportunidad. El Archivo conserva siglos de palabras. Una parte está digitalizada; otra puede transformarse en datos. Si el proyecto funciona, una consulta ya no devolverá solamente documentos existentes. La máquina podrá producir una continuación nueva a partir de lo aprendido en ellos.

La archivista lee primero la sección dedicada a las fuentes.

Pregunta qué colecciones serán incluidas, quién autorizó esos usos, cómo se registrará la procedencia y qué ocurrirá si una comunidad retira su permiso. El equipo responde con cifras de volumen, formatos admitidos y métodos para eliminar duplicados.

Las respuestas no coinciden con las preguntas.

Alguien propone comenzar por todo lo técnicamente accesible y resolver excepciones después. La grabación de la canción ya está convertida a texto parcial. Sería apenas una secuencia entre millones.

La archivista marca la restricción.

El consentimiento permitía consulta familiar e investigación de procedencia. No permitía entrenamiento.

La cinta queda afuera.

Una ingeniera lamenta perder un ejemplo valioso de transmisión oral. La archivista responde que un sistema incapaz de respetar una ausencia no está aprendiendo a recibir voces.

Está aprendiendo a disponer de ellas.

### El corpus no es la humanidad

La colección final es inmensa.

No es total.

Contiene enciclopedias y recetas, tratados y bromas, documentación técnica, novelas, foros, leyes, poemas, subtítulos y fragmentos de programas. Algunas obras fueron seleccionadas con cuidado. Otras llegaron dentro de grandes conjuntos reunidos para fines distintos. Unas poseen autoría y licencia claras; otras arrastran procedencias incompletas.

Llamarla *archivo de la humanidad* resulta tentador.

También resulta engañoso.

No todas las personas pudieron escribir. No todas las lenguas fueron digitalizadas en la misma proporción. Hay comunidades cuya memoria vive en prácticas, territorios, gestos o formas orales que ningún rastreador encuentra. Hay cartas destruidas, bibliotecas saqueadas, conocimientos protegidos y conversaciones que nunca debieron abandonar la habitación donde ocurrieron.

Incluso la red pública no representa de manera uniforme a quienes la usan. Publican más quienes poseen conexión, tiempo, alfabetización, seguridad y plataformas dispuestas a conservar sus palabras. Algunos textos se copian miles de veces; otros existen en una página que ningún recolector visita. El volumen puede convertir la repetición en apariencia de consenso.

El corpus contiene rastros humanos.

No contiene a la humanidad.

Esta diferencia no es modestia retórica. Define qué aprenderá el sistema. Una lengua abundante dispondrá de más ejemplos. Una asociación repetida —aunque sea un prejuicio— resultará más fácil de reproducir. Una experiencia poco documentada aparecerá como rara, incierta o invisible.

Los datos no llegan en estado natural.

Alguien decide dónde buscar, qué formato aceptar, qué filtrar, cómo identificar un idioma y cuándo dos documentos cuentan como duplicados. Alguien define qué material resulta dañino, privado, ilegal, irrelevante o demasiado costoso de procesar. Incluso la decisión de reunir «todo lo posible» contiene una política: favorece aquello que el mundo ya volvió posible capturar.

La colección no es un espejo neutral de la especie.

Es una historia de accesos convertida en entrenamiento.

### Romper las palabras

La máquina no recibe libros como una lectora.

Antes del entrenamiento, el texto se transforma en unidades llamadas *tokens*. Un token puede coincidir con una palabra frecuente, una parte de palabra, un signo de puntuación o una secuencia de caracteres. La división depende del sistema utilizado y de los patrones disponibles en los datos.

Una palabra rara puede partirse en varias piezas.

Un término común puede permanecer unido.

Idiomas distintos encuentran costos distintos en esa fragmentación. Una frase breve para una persona puede ocupar muchas unidades para el modelo si su escritura o su lengua estuvieron menos representadas al construir el vocabulario.

Cada token se convierte en un número y luego en una representación matemática que cambiará durante el aprendizaje. El sistema no conserva la tinta, la voz, el papel ni el cuerpo que produjo la frase. Recibe una secuencia formal y una posición dentro de ella.

Esto no vuelve insignificante al lenguaje.

Vuelve visible la distancia entre la experiencia humana y el material de entrenamiento.

La palabra *río* pudo ser orientación, frontera, recuerdo de infancia o derecho disputado. En la entrada del modelo es un token o una combinación de tokens. Su relación con otros usos sólo podrá aparecer mediante las regularidades del conjunto: qué verbos la rodean, qué imágenes la acompañan, en qué documentos figura y qué continuaciones reduce o aumenta su probabilidad.

La máquina no comienza sabiendo qué es un río.

Comienza recibiendo diferencias entre signos.

Lo que pueda construir a partir de ellas será una pregunta empírica sobre su comportamiento y una pregunta filosófica sobre qué estamos dispuestas a llamar comprensión. Ninguna de las dos queda resuelta sólo porque el sistema use la palabra correctamente.

### Aprender a continuar

Durante el entrenamiento ocurre una tarea repetida a una escala difícil de imaginar.

El sistema recibe una secuencia incompleta e intenta predecir el token siguiente. Compara sus probabilidades con el token que efectivamente aparecía en el texto. El error modifica muchos parámetros internos. Luego recibe otra secuencia y vuelve a intentarlo.

Una vez.

Millones de veces.

Muchísimas más.

La instrucción parece pobre: **continuá**.

Pero para continuar con menor error, el sistema encuentra útil representar regularidades de varios niveles. Debe reconocer dependencias gramaticales, usos de palabras, estructuras de código, convenciones de género y relaciones que atraviesan largas distancias dentro del contexto. Una pregunta suele preparar cierto tipo de respuesta; una llave abierta en un programa exige alguna forma de cierre; un personaje mencionado antes limita quién puede hablar después.

Las arquitecturas llamadas *transformers* hicieron posible modelar muchas de esas relaciones mediante mecanismos de atención. En términos simplificados, distintas partes de la red aprenden a ponderar qué posiciones anteriores resultan relevantes para procesar cada token. No existe un único foco que mira como una conciencia. Existen operaciones paralelas que transforman representaciones según relaciones aprendidas.

La atención técnica no es atención ética.

Puede relacionar una promesa con su antecedente sin sentirse obligada por ella. Puede completar la forma de una condolencia sin haber perdido a nadie. Llamar atención a ambos fenómenos es una coincidencia fértil del lenguaje, no prueba de que sean la misma capacidad.

El objetivo de predecir lo siguiente tampoco describe por sí solo todo lo que el sistema termina siendo capaz de hacer. Una regla sencilla aplicada a datos y arquitecturas complejas puede producir representaciones útiles para resumir, traducir, responder preguntas, escribir código y seguir instrucciones después de etapas adicionales de entrenamiento.

Decir *sólo predice tokens* puede ser técnicamente cierto y explicativamente insuficiente.

Decir *por eso entiende como nosotras* agrega una conclusión que el rendimiento no demuestra.

Entre ambas frases queda el trabajo de investigar qué capacidades aparecieron, cómo fallan y qué clase de sistema las realiza.

### Una compresión sin estantes

Cuando termina una etapa de entrenamiento, los documentos no están ordenados dentro del modelo como libros diminutos.

No hay un anaquel para la poesía, otro para el código y un cajón donde aguardan cartas completas. Lo que permanece es una configuración de parámetros: números ajustados de manera distribuida por innumerables ejemplos.

Llamar a eso **compresión** puede iluminar y confundir.

Ilumina porque una estructura mucho menor que el conjunto de entrenamiento conserva regularidades que permiten producir secuencias semejantes, completar patrones y responder de maneras que dependen de lo aprendido. La forma exacta de cada documento suele perderse mientras persisten relaciones reutilizables.

Confunde si imaginamos una copia codificada que podría descomprimirse fielmente para recuperar cualquier obra original. Un modelo de lenguaje no funciona, en general, como un archivo comprimido convencional. Genera según probabilidades condicionadas por el contexto; puede mezclar patrones, inventar detalles o responder sin una fuente identificable.

La compresión es una metáfora funcional.

No una descripción literal de propiedad ni memoria.

Una biblioteca puede decir de qué volumen obtuvo una frase. Un modelo paramétrico no conserva necesariamente una ruta interpretable desde cada respuesta hasta los textos que contribuyeron a formarla. Aunque una idea provenga de muchas obras, la salida no trae por sí sola notas al pie.

Por eso la fluidez puede producir una ilusión de procedencia.

La máquina formula una afirmación con el tono de alguien que recuerda. En realidad, puede estar generando una continuación plausible, combinando regularidades o reproduciendo un fragmento. Sin herramientas externas de búsqueda y verificación, la seguridad de la prosa no distingue esos casos.

El archivo tradicional podía perder una fuente.

El modelo aprende a hablar desde una estructura donde la fuente suele no aparecer.

### Lo que vuelve literalmente

La pérdida de procedencia no significa que todo documento se disuelva por completo.

Los modelos pueden memorizar secuencias y, bajo ciertas condiciones, reproducir material de entrenamiento de forma literal o casi literal. La repetición de un ejemplo, la capacidad del modelo y características inusuales de una secuencia pueden aumentar ese riesgo. Investigaciones han mostrado que es posible extraer de algunos modelos fragmentos que contienen código, conversaciones o información personal.

No se sigue que cada respuesta sea una cita oculta.

Tampoco que el entrenamiento sea incapaz de generalizar.

Memorización y aprendizaje de regularidades pueden coexistir. El problema ético aparece precisamente porque no siempre sabemos de antemano qué fragmento quedará como patrón distribuido y cuál podrá regresar con demasiada fidelidad.

Una dirección, una confesión o una obra no dejan de requerir cuidado porque hayan sido convertidas en números durante el proceso. La transformación técnica no lava la procedencia.

El equipo implementa filtros, elimina ciertos datos personales detectables, reduce duplicaciones y prueba si el modelo reproduce secuencias sensibles. Ninguna medida ofrece garantía absoluta. Los filtros cometen errores; los detectores no reconocen todos los contextos; una cadena inocua en un documento puede identificar a alguien dentro de otro.

La archivista agrega una condición: los incidentes de memorización no serán tratados sólo como fallas de rendimiento. Tendrán procedimientos de reporte, investigación, mitigación y respuesta para las personas afectadas.

Olvidar no es una capacidad automática del modelo.

Debe convertirse en una obligación del sistema que lo entrena y despliega.

### Público no significa entregado

Una gran parte del corpus proviene de materiales accesibles.

La palabra *público* parece resolver la cuestión. Si cualquiera podía leer una página, ¿por qué una máquina no podría aprender de ella?

Pero acceso, legalidad, licencia, expectativa y consentimiento no son sinónimos.

Una conversación publicada para recibir apoyo no fue necesariamente ofrecida para entrenar un producto. Una obra disponible para lectura conserva autoría y condiciones de uso. Un sitio puede ser técnicamente accesible y prohibir recolección automatizada. Las leyes aplicables difieren entre lugares, clases de material y finalidades; la respuesta jurídica no sustituye por sí sola la pregunta ética.

Tampoco es viable solicitar permiso individual retroactivo para cada línea de todos los conjuntos históricos. La escala plantea problemas reales que no desaparecen mediante una consigna moral sencilla.

Por eso importan la documentación de fuentes, las licencias, las vías de exclusión cuando sean posibles, los mecanismos de reclamo, la protección de datos, la negociación colectiva y el poder de las comunidades sobre materiales que no pueden reducirse a una suma de autores individuales.

Un corpus responsable no será puro.

Será discutible, trazable y capaz de corregirse.

El equipo publica una ficha de datos que describe categorías, períodos, lenguas, filtros y limitaciones conocidas. No enumera cada texto cuando hacerlo expondría información o resultaría impracticable, pero tampoco se esconde detrás del tamaño para afirmar que el origen ya no importa.

La transparencia no repara por sí sola usos injustos.

Permite al menos que la escala no funcione como secreto.

### Las manos alrededor de la máquina

La expresión *la máquina aprendió* comprime otro conjunto de trabajos.

Personas diseñaron la arquitectura, reunieron y limpiaron datos, mantuvieron equipos, definieron objetivos, corrigieron fallos y evaluaron resultados. Otras etiquetaron respuestas, compararon salidas, documentaron conductas peligrosas y escribieron ejemplos de cómo seguir instrucciones. Centros de datos consumieron energía y agua bajo condiciones materiales concretas.

Después del entrenamiento inicial vinieron nuevas etapas.

Un modelo que sólo continúa texto puede completar una pregunta con otra pregunta, imitar formatos dañinos o ignorar la intención de quien lo usa. Para convertirlo en asistente, el equipo utiliza demostraciones, preferencias humanas, reglas y evaluaciones. Esas capas orientan qué respuestas se premian, cuáles se rechazan y qué clase de voz aparecerá ante una solicitud.

No existe una salida puramente producida por los datos.

Hay decisiones de diseño antes, durante y después.

También hay trabajo que el relato tecnológico vuelve invisible. Una etiqueta no cae del cielo. Alguien tuvo que leer material repetitivo, violento o íntimo para clasificarlo. Una política de seguridad contiene juicios acerca del daño, y esos juicios pueden proteger, censurar, discriminar o fallar de maneras que afectan de forma desigual.

La máquina no surge sola del archivo.

Es construida por una organización de personas, recursos e intereses alrededor del archivo.

Esa organización forma parte de lo que responde.

### La primera continuación

Meses después, el equipo presenta el modelo.

La sala es la misma donde la mujer y la archivista escucharon la cinta. Esta vez hay más cables, varias pantallas y personas de pie junto a las paredes. En el centro aparece un campo vacío esperando texto.

La muchacha escribe:

**Una voz cruza el río y descubre que…**

La máquina calcula una distribución de posibilidades. Elige un token. Después otro. Cada elección modifica el contexto para la siguiente.

En la pantalla aparece una frase:

**…la otra orilla también había aprendido su nombre.**

Nadie encuentra esa oración en los índices disponibles del corpus.

Podría estar demasiado cerca de un texto no detectado. Podría combinar imágenes comunes de miles de relatos. Podría ser una continuación nueva en un sentido suficiente para la conversación y derivada en un sentido suficiente para negar todo origen soberano.

La sala guarda silencio.

La frase no demuestra conciencia. No prueba que la máquina sepa qué es un río, una voz o un nombre. Demuestra algo más limitado y, aun así, extraordinario: el sistema ha aprendido regularidades capaces de producir una continuación pertinente que ninguna participante eligió palabra por palabra.

El **archivo vivo** conserva procedencias, límites y derecho a impugnar sus usos. Reconoce que toda colección es parcial y que transformar rastros en capacidad no cancela obligaciones hacia quienes los produjeron.

El **archivo fosilizado** llama humanidad a lo que logró capturar. Trata acceso como consentimiento, escala como absolución y fluidez como prueba de verdad. Cuando una voz falta, concluye que no tenía nada que decir.

La máquina espera otra entrada.

Dentro de sus parámetros no habla una autora única. Tampoco habla literalmente una multitud consciente. Hay regularidades sedimentadas por textos humanos y orientadas por decisiones técnicas que ahora pueden organizarse en una secuencia no escrita de antemano.

El archivo ha dejado de limitarse a devolver documentos.

Ha comenzado a formar frases.

La pregunta siguiente ya no será sólo qué contiene.

Será quién —o qué— habla cuando responde.
