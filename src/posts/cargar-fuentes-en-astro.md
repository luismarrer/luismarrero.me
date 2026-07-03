---
title: "Cómo cargar fuentes correctamente en Astro y en proyectos web modernos"
published: true
description: "Por qué auto-hospedar fuentes en WOFF2 con @font-face es la práctica recomendada hoy, qué cambió con el particionamiento de caché en los navegadores, y cómo aplicarlo en un proyecto Astro."
tags: ["Astro", "CSS", "Rendimiento", "Tipografía"]
date: "Jul 3 2026"
---

Cargar una fuente parece un detalle menor: dos líneas en el `<head>` y el sitio ya se ve como uno quiere. Pero pocas decisiones tan pequeñas tocan tantas dimensiones a la vez. La tipografía afecta el rendimiento (las fuentes suelen estar en la ruta crítica del renderizado), la privacidad (según de dónde se sirvan), el control (qué se cachea, con qué cabeceras, con qué disponibilidad), la experiencia visual (destellos de texto invisible o sin estilo durante la carga) y el mantenimiento a largo plazo del proyecto.

El patrón más común sigue siendo copiar un `<link>` desde Google Fonts porque es rápido y funciona. Este artículo defiende una postura distinta: una web cuidada debe tratar sus fuentes como lo que son —assets propios— y optimizarlas con el mismo criterio que aplicaría a sus imágenes o a su JavaScript. La tesis concreta: **en proyectos web modernos, lo recomendable es auto-hospedar las fuentes en formato WOFF2, declararlas con `@font-face`, cargar solo los pesos necesarios y evitar depender de la API remota de Google Fonts**, salvo que exista una razón muy específica para lo contrario.

No es una posición dogmática. Es la consecuencia de cambios reales en cómo funcionan los navegadores desde alrededor de 2020, y de que las ventajas históricas de las CDNs de fuentes —que existieron y fueron legítimas— hoy son mucho menores o directamente inexistentes.

## La forma común, pero ya no ideal

El punto de partida habitual es este:

```html
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
  rel="stylesheet"
/>
```

Esto funciona, y funciona razonablemente bien: Google sirve un CSS generado dinámicamente desde `fonts.googleapis.com`, que a su vez apunta a los archivos de fuente en `fonts.gstatic.com`. El servicio negocia formatos, aplica `unicode-range` para dividir por subsets y se apoya en una CDN global.

El problema no es que esté roto, sino lo que implica aceptar por defecto:

- **Añade una dependencia externa** a la disponibilidad y las decisiones de un tercero. Si Google cambia el comportamiento del endpoint, o el visitante está en una red que bloquea sus dominios, la tipografía del sitio deja de estar bajo tu control.
- **Obliga a resolver DNS y establecer conexiones nuevas** hacia dos dominios ajenos (`fonts.googleapis.com` y `fonts.gstatic.com`), con su coste de DNS, TCP y TLS. Una fuente auto-hospedada viaja por la conexión HTTP/2 o HTTP/3 que el navegador ya tiene abierta con tu servidor.
- **Reduce el control sobre caché y cabeceras.** No decides los `Cache-Control`, no puedes versionar los archivos con tu pipeline de build, y no puedes garantizar que lo servido hoy sea idéntico a lo servido mañana.
- **Tiene implicaciones de privacidad.** Cada visita transmite la dirección IP del visitante a servidores de Google. En la Unión Europea esto dejó de ser una preocupación teórica: en enero de 2022 un tribunal regional de Múnich resolvió que incrustar Google Fonts de forma remota, sin consentimiento, vulneraba el RGPD precisamente por esa transmisión de la IP.
- **Puede contribuir a FOUC/FOUT** si no se maneja con cuidado: el navegador primero descarga el CSS remoto, y solo entonces descubre qué archivos de fuente necesita. Esa cadena de peticiones retrasa el momento en que el texto adopta su forma definitiva.
- **Limita la granularidad.** Decides familia y pesos en la URL, pero no qué archivos exactos se sirven, ni cómo se llaman, ni cómo se agrupan los subsets más allá de lo que el servicio decida.

Durante años, estos costes se compensaban con ventajas reales. Hoy —como veremos en la sección histórica— esas ventajas se han erosionado, y usar el `<link>` remoto por defecto es más una comodidad heredada que una decisión técnica fuerte. Sigue siendo una opción válida en ciertos contextos, pero no debería ser el punto de partida de un proyecto serio, salvo que estés priorizando la comodidad inmediata por encima del control técnico.

## La forma recomendada: auto-hospedar fuentes en WOFF2

El flujo recomendado es corto y se hace una sola vez por proyecto:

1. Obtener la fuente en formato `.woff2` (descargándola ya convertida, o convirtiéndola desde `.ttf`/`.otf`).
2. Colocar los archivos dentro del proyecto.
3. Declarar cada peso y estilo con `@font-face`.
4. Definir `font-display` explícitamente.
5. Cargar únicamente los pesos y estilos que el diseño usa de verdad.
6. Opcionalmente, precargar con `<link rel="preload">` solo la fuente crítica.

### En Astro: el método manual y portable

Astro sirve todo lo que está en `public/` directamente desde la raíz del sitio, sin procesarlo [6]. Eso convierte a `public/fonts/` en el lugar natural para los archivos de fuente: URLs estables y predecibles, sin pasar por el bundler.

```txt
public/
  fonts/
    inter-regular.woff2
    inter-bold.woff2

src/
  styles/
    fonts.css
    global.css
```

Las declaraciones viven en un `fonts.css` dedicado. Cada peso es un bloque `@font-face` independiente que apunta a su archivo:

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-bold.woff2") format("woff2");
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
```

Y se importan una sola vez en el layout base, para que apliquen a todo el sitio:

```astro
---
import "../styles/fonts.css";
import "../styles/global.css";
---

<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <title>Mi sitio</title>
  </head>
  <body>
    <slot />
  </body>
</html>
```

Con esto, el navegador descubre las fuentes en el primer CSS que descarga, las pide a tu propio dominio por la conexión ya establecida, y tú controlas nombres de archivo, cabeceras de caché y versionado.

Conviene saber que Astro también mantiene documentación moderna sobre fuentes y que, según la versión del proyecto, existen APIs más integradas para gestionarlas desde la configuración [7]. Este artículo se centra deliberadamente en el método manual porque es **portable, explícito y no depende de ningún framework**: lo que se describe aquí funciona igual en Astro, en un sitio estático plano o en cualquier otro stack. Entender el mecanismo manual, además, es lo que permite evaluar con criterio cualquier abstracción que se construya encima.

## Por qué WOFF2

WOFF2 (Web Open Font Format 2) es el formato que deberías usar en producción, y en navegadores modernos, el único. Las razones:

- **Mejor compresión.** WOFF2 usa compresión Brotli y logra archivos notablemente más pequeños que WOFF, que a su vez ya era más pequeño que los formatos de escritorio. Menos bytes transferidos significa texto definitivo antes.
- **Soporte universal en navegadores modernos.** Todos los navegadores relevantes lo soportan desde hace años. La época en que había que servir una cascada de formatos alternativos terminó.
- **Simplifica el `@font-face`.** No hay motivo para incluir `.ttf`, `.otf`, `.eot` o fuentes `.svg` como fallback en producción: son archivos más pesados que ningún navegador actual va a necesitar, y mantenerlos es ruido. La guía de buenas prácticas de fuentes de web.dev es explícita en este punto: usa WOFF2 y olvídate de los formatos antiguos si tu público usa navegadores modernos [5].

Los formatos `.ttf` y `.otf` siguen siendo relevantes como *formato de origen* —es lo que suelen distribuir las fundiciones tipográficas— pero su lugar es tu carpeta de trabajo, no tu servidor de producción.

## Herramientas prácticas

### Convertir fuentes a WOFF2

Si tienes una fuente en `.ttf` o `.otf` (comprada, o descargada de la fundición), **CloudConvert** resuelve la conversión a `.woff2` sin instalar nada. Para flujos automatizados, las herramientas de línea de comandos del propio proyecto WOFF2 de Google o `fonttools` hacen lo mismo de forma reproducible.

Una advertencia que no es opcional: **verifica la licencia antes de convertir y publicar**. Las fuentes bajo SIL Open Font License permiten auto-hospedaje y conversión sin problema, pero muchas licencias comerciales restringen el uso web, limitan los formatos o exigen una licencia web específica. Convertir un `.otf` de escritorio a WOFF2 y subirlo a un servidor público puede ser una infracción de licencia aunque la fuente se haya comprado legítimamente.

### Auto-hospedar fuentes de Google Fonts

Que no convenga usar la API remota de Google Fonts no significa renunciar a su catálogo: las fuentes de Google Fonts son de licencia abierta y pueden auto-hospedarse.

**Google Webfonts Helper** es la herramienta clásica para esto: permite buscar cualquier fuente del catálogo, seleccionar los pesos, estilos y subsets que necesitas, y descargar directamente los archivos `.woff2` junto con el bloque de CSS `@font-face` de referencia. El resultado es exactamente lo que este artículo recomienda: los mismos diseños tipográficos de Google Fonts, servidos desde tu dominio, sin ninguna petición a la infraestructura de Google en producción.

## Nota histórica: por qué antes sí tenía sentido usar Google Fonts

Sería deshonesto presentar la recomendación actual sin reconocer que, durante buena parte de la década de 2010, usar Google Fonts era una decisión técnicamente sólida. Los argumentos eran reales:

**El caché compartido entre sitios.** Miles de sitios referenciaban exactamente las mismas URLs de `fonts.gstatic.com`. Como el caché HTTP del navegador se indexaba únicamente por URL, un visitante que ya hubiera cargado Roboto en cualquier otro sitio la tenía cacheada al llegar al tuyo: la fuente costaba, en la práctica, cero bytes. Cuanto más popular la fuente, más probable el acierto de caché.

**Una CDN global de primer nivel.** Servidores de Google cerca de cualquier usuario del mundo, en una época en que contratar una CDN propia era caro y complejo. Para un sitio pequeño alojado en un único servidor, la CDN de Google era objetivamente más rápida para usuarios lejanos.

**Compatibilidad automática.** El endpoint de CSS inspeccionaba el *user agent* y servía a cada navegador el formato que entendía: EOT para Internet Explorer antiguo, TTF, WOFF o WOFF2 según el caso. En la era de la fragmentación de formatos, delegar esa matriz de compatibilidad era un alivio genuino.

El tercer argumento murió de éxito: la convergencia universal en WOFF2 lo volvió innecesario. El segundo se ha atenuado: el hosting moderno (Netlify, Vercel, Cloudflare Pages, y en general cualquier plataforma donde se despliega un sitio Astro) ya sirve los assets estáticos desde una CDN. Pero el primero —el más citado y el más convincente— no se desvaneció gradualmente: lo eliminaron los propios navegadores, de forma deliberada, por razones de privacidad. Eso merece su propia sección.

## El particionamiento de caché: cuándo dejó de aplicar el beneficio del caché compartido

Durante la mayor parte de la historia de la web, el caché HTTP del navegador funcionó como un espacio único indexado por URL: si el recurso `https://fonts.gstatic.com/.../inter.woff2` estaba cacheado, cualquier página de cualquier sitio podía reutilizarlo. Este diseño es el que sustentaba el argumento del "probablemente el usuario ya tiene esta fuente".

El problema es que ese mismo diseño filtraba información entre sitios. Midiendo si un recurso carga instantáneamente (caché) o tarda (red), un sitio podía inferir qué otros sitios había visitado el usuario; y almacenando marcas identificables en recursos cacheados, un tercero presente en muchos sitios podía reidentificar al usuario a través de ellos sin usar cookies —las llamadas *supercookies*. El caché compartido era, simultáneamente, una optimización de rendimiento y un canal de rastreo.

La respuesta de los navegadores fue **particionar**: dejar de indexar el caché solo por URL y pasar a indexarlo por una clave compuesta que incorpora el contexto de navegación de nivel superior. Con caché particionado, la fuente de `fonts.gstatic.com` cargada dentro de `sitio-a.com` y la misma fuente cargada dentro de `sitio-b.com` son entradas de caché distintas. La reutilización entre sitios desaparece por diseño.

La cronología, con precisión:

- **WebKit/Safari fue temprano.** WebKit venía aplicando particiones y restricciones anti-rastreo desde años antes que el resto; sus publicaciones sobre Intelligent Tracking Prevention —como la de ITP 2.1, de 2019— ya se apoyaban en la noción de cachés particionadas como parte de su modelo de aislamiento [4]. No hubo una fecha única de "encendido" en Safari comparable a la de los demás: fue una postura sostenida que se fue endureciendo.
- **Chrome particionó su caché HTTP en Chrome 86**, alrededor de octubre de 2020. El artículo de Chrome Developers "Gaining security and privacy by partitioning the cache" documenta el cambio: el caché pasó de indexarse por URL a indexarse con una clave más amplia que incorpora el contexto de sitio (la *Network Isolation Key*, que incluye el sitio de nivel superior), precisamente para cerrar los ataques de sondeo de caché y el rastreo cross-site [1].
- **Firefox incorporó Network Partitioning en Firefox 85**, en enero de 2021. El anuncio del blog de seguridad de Mozilla, "Firefox 85 Cracks Down on Supercookies", explica que el objetivo era neutralizar las supercookies basadas en caché, particionando no solo el caché HTTP sino un conjunto amplio de estado de red por sitio de nivel superior [2]. MDN documenta Network Partitioning como habilitado por defecto en Firefox desde esa versión [3].

Más que un apagón en una fecha exacta, fue una transición progresiva: WebKit ya había avanzado temprano en la partición de cachés; Chrome cambió su caché HTTP en Chrome 86; Firefox incorporó Network Partitioning en Firefox 85. En la práctica, desde ese periodo el viejo argumento de "probablemente el usuario ya tiene esa fuente cacheada desde otro sitio" dejó de ser una base sólida para decidir usar Google Fonts en producción. Si se quiere una formulación general —"para 2022, el beneficio del caché compartido cross-site había dejado de ser una razón de peso para usar CDNs de fuentes"—, debe entenderse como lo que es: una conclusión práctica derivada de la adopción de particionamiento de caché, red y estado por parte de los navegadores principales, no una fecha oficial única que alguno de ellos haya declarado.

La consecuencia para este artículo es directa: hoy, la primera visita de cada usuario a tu sitio descarga la fuente desde cero, se sirva desde Google o desde tu dominio. Y si el coste de descarga es el mismo, servirla desde tu dominio es estrictamente mejor: sin resolución DNS adicional, sin handshake TLS extra, sin transmisión de la IP del visitante a un tercero, y con control total sobre caché y versionado.

## Recomendaciones concretas

Destiladas de todo lo anterior:

- **Usa WOFF2, y solo WOFF2**, en producción para navegadores modernos.
- **Auto-hospeda las fuentes** como assets del propio proyecto.
- **Carga solo los pesos y estilos que el diseño usa.** Cada peso es un archivo; cuatro pesos "por si acaso" son cientos de kilobytes de más. Regular y bold bastan para la mayoría de los sitios de contenido. (Si necesitas muchos pesos, considera una fuente variable: un solo archivo cubre todo el eje de peso.)
- **Usa subsets cuando tenga sentido.** Si tu contenido es solo alfabeto latino, no sirvas cirílico, griego ni vietnamita. Herramientas como Google Webfonts Helper permiten elegir el subset al descargar, y `unicode-range` en el `@font-face` permite dividir por rangos si sirves varios.
- **Declara `font-display` siempre.** `swap` es el valor por defecto razonable: el texto es visible de inmediato con la fuente de respaldo y cambia cuando la webfont llega. `optional` puede ser mejor cuando priorizas la estabilidad visual sobre la fidelidad tipográfica: da al navegador un margen muy breve para usar la webfont y, si no llega a tiempo, mantiene la de respaldo sin intercambio posterior —cero *layout shift*, a cambio de que algunos visitantes de primera visita vean la fuente del sistema.
- **Usa `preload` solo para la fuente crítica** above-the-fold (típicamente la del cuerpo de texto en su peso regular):

```html
<link
  rel="preload"
  href="/fonts/inter-regular.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
```

  Dos matices. Primero, el atributo `crossorigin` es obligatorio aunque la fuente sea de tu propio dominio: las fuentes se descargan en modo CORS anónimo, y sin ese atributo el preload no coincide con la petición real y el navegador descarga el archivo dos veces. Segundo, `preload` no es magia: le dice al navegador que ese recurso importa *más* que otros, y el ancho de banda no es infinito. Precargar tres o cuatro fuentes compite con el CSS, el LCP y todo lo demás que es crítico. Precargar todo equivale a no priorizar nada.

- **No uses `@import` remoto de Google Fonts** en el CSS: encadena descargas en serie (CSS → CSS remoto → fuente) y es la peor variante posible en rendimiento.
- **Revisa las licencias** antes de convertir o publicar cualquier fuente.
- **Mantén un `fonts.css` organizado**: un archivo dedicado, un bloque por peso/estilo, nombres de archivo consistentes. Es documentación de la tipografía del proyecto además de código.

## Cuándo puede seguir teniendo sentido la API de Google Fonts

Nada de lo anterior justifica el fanatismo. La API remota de Google Fonts sigue siendo una opción razonable cuando:

- estás haciendo un **prototipo rápido** y quieres probar tipografías sin ceremonia;
- se trata de una **demo temporal** o un experimento que no llegará a producción;
- es un **proyecto interno** sin exigencias de rendimiento ni de privacidad;
- explícitamente **no quieres gestionar assets**, y ese tradeoff de mantenimiento pesa más que el control en tu contexto.

Son casos legítimos: la fricción cero de un `<link>` tiene valor real cuando el proyecto es descartable o el criterio dominante es la velocidad de iteración. Pero para un proyecto serio —un portafolio profesional, un sitio de producción, un producto donde el rendimiento o la privacidad importan—, auto-hospedar WOFF2 es preferible, y el coste de hacerlo bien es de una tarde, una sola vez.

## Conclusión

Cargar fuentes bien es una de esas decisiones pequeñas que revelan criterio técnico. No exige herramientas sofisticadas ni conocimiento arcano: exige entender qué hace el navegador, qué cambió en los últimos años y qué se gana con cada elección. No se trata solo de estética; se trata de rendimiento medible, de privacidad de los visitantes y de control sobre los propios assets.

En Astro, además, hacerlo bien es trivial: una carpeta en `public/fonts`, un `fonts.css` con dos bloques `@font-face`, una importación en el layout. La web moderna premia sistemáticamente tener menos dependencias externas innecesarias — menos dominios que resolver, menos terceros en los que confiar, menos comportamiento que no controlas. Las fuentes son un buen lugar para empezar a cobrar ese premio.

## Referencias

[1] Chrome Developers — "Gaining security and privacy by partitioning the cache". https://developer.chrome.com/blog/http-cache-partitioning

[2] Mozilla Security Blog — "Firefox 85 Cracks Down on Supercookies". https://blog.mozilla.org/security/2021/01/26/supercookie-protections/

[3] MDN Web Docs — "State Partitioning". https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/State_Partitioning

[4] WebKit Blog — "Intelligent Tracking Prevention 2.1". https://webkit.org/blog/8613/intelligent-tracking-prevention-2-1/

[5] web.dev — "Best practices for fonts". https://web.dev/articles/font-best-practices

[6] Astro Docs — "Project structure", sección sobre el directorio `public/`. https://docs.astro.build/en/basics/project-structure/

[7] Astro Docs — "Fonts" (guía de fuentes, incluida la API integrada de versiones recientes). https://docs.astro.build/en/guides/fonts/
