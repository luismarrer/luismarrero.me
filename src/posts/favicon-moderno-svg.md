---
title: "El favicon también evolucionó: por qué ahora prefiero SVG"
published: true
description: "El .ico no está muerto, pero ya no debería ser el protagonista. Por qué una estrategia moderna de favicon empieza por SVG, cómo adaptarlo al modo oscuro, y qué generar con RealFaviconGenerator."
tags: ["Frontend", "SVG", "HTML", "Diseño"]
date: "Jul 3 2026"
---

Durante años traté el favicon como un trámite: exportar un `favicon.ico`, tirarlo en la raíz del proyecto y no volver a pensarlo. Hasta que empecé a fijarme en cómo lo hacen los proyectos modernos —incluyendo varios de [Midudev](https://x.com/midudev/status/1891904012963688726)— y noté algo curioso: el archivo principal ya no era un `.ico`, sino un `favicon.svg`. Lo que parecía un detalle viejo y resuelto resulta que evolucionó en silencio, y vale la pena entender cómo.

La conclusión a la que llegué, y que quiero dejar anotada aquí: **el `.ico` no está muerto, pero ya no debería ser el centro de la estrategia. Hoy tiene más sentido pensar "SVG first"**, añadir PNGs, Apple touch icon y manifest según lo que el proyecto necesite, y dejar el `.ico` como un fallback opcional para compatibilidad extrema.

## Qué es un favicon y por qué importa

El favicon es el ícono diminuto que identifica a un sitio. Aparece en más lugares de los que uno registra conscientemente: la pestaña del navegador, los bookmarks, el historial, los resultados de búsqueda, los accesos directos en el móvil, las apps web instaladas.

Es pequeño, pero hace un trabajo desproporcionado para su tamaño. Cuando tienes veinte pestañas abiertas, el favicon *es* tu sitio: es lo único que el usuario ve para encontrarte. Un sitio sin favicon (o con el ícono genérico del framework) transmite lo mismo que una tienda sin letrero — que nadie se detuvo a cuidar ese detalle.

## El legado de favicon.ico

El formato `.ico` viene de otra era de la web: Internet Explorer lo introdujo a finales de los noventa, y los navegadores lo buscaban por convención en `/favicon.ico`, sin necesidad de declararlo. Durante mucho tiempo fue el estándar de facto, y en su momento tenía sentido: es un formato contenedor que puede guardar **varios tamaños dentro del mismo archivo** (16×16, 32×32, 48×48), de modo que cada contexto usa la versión que le corresponde.

Todo eso sigue funcionando. La compatibilidad del `.ico` es prácticamente universal, y ningún navegador va a dejar de soportarlo pronto. El punto no es que esté roto — es que ya no es necesario que sea el formato *principal*. Los navegadores modernos entienden formatos mejores, y seguir empezando por `.ico` es más inercia que decisión técnica.

## Por qué SVG es la opción moderna

Un favicon SVG tiene ventajas difíciles de ignorar:

- **Es vectorial**: escala a cualquier tamaño sin pixelarse. Un solo archivo cubre desde los 16×16 de una pestaña hasta lo que venga.
- **Suele ser más liviano**: para un logo simple, unas cuantas líneas de markup pesan menos que un `.ico` con tres bitmaps dentro.
- **Es editable como código**: cambiar un color o ajustar una forma es editar texto, no reabrir un editor gráfico y re-exportar.
- **Es ideal para logos simples**, que es exactamente lo que un favicon debería ser — a 16 píxeles no hay espacio para sutilezas.

Y usarlo no tiene misterio:

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
```

## La ventaja más interesante: modo claro y modo oscuro

Esto fue lo que me terminó de convencer. Un SVG puede llevar CSS interno, y ese CSS puede responder a media queries — incluida `prefers-color-scheme`. Es decir: **el mismo archivo puede verse de un color en modo claro y de otro en modo oscuro**, sin JavaScript ni archivos duplicados.

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <style>
    path {
      fill: black;
    }

    @media (prefers-color-scheme: dark) {
      path {
        fill: white;
      }
    }
  </style>

  <path d="M50 10 L90 90 H10 Z" />
</svg>
```

Un triángulo negro sobre pestañas claras, blanco sobre pestañas oscuras. El mismo archivo.

Aquí conviene ser preciso: con PNG o ICO el archivo en sí es estático — un bitmap no puede decidir nada. Existen estrategias alternativas: servir varios archivos con `media` en los `<link>`, o cambiar el favicon con JavaScript escuchando el esquema de color. Funcionan, pero son más piezas móviles. El SVG resuelve el problema *dentro del propio archivo*, que es la solución más elegante de las tres.

Una advertencia honesta: los navegadores cachean favicons de forma agresiva y no todos evalúan la media query en el mismo momento, así que el comportamiento puede variar. Antes de dar por hecho que funciona, pruébalo en los navegadores que te importen.

## RealFaviconGenerator: para no olvidar ninguna pieza

"SVG first" no significa "SVG y nada más". Según el proyecto, hay contextos que todavía piden otros archivos, y aquí es donde me resultó muy útil [RealFaviconGenerator](https://realfavicongenerator.net/): le das tu imagen y genera el paquete completo, con el HTML listo para pegar.

Lo que aporta no es magia, es *checklist*. Te evita olvidar casos como:

- el **favicon SVG** como pieza principal,
- los **PNGs** en tamaños clásicos (32×32, 16×16) para navegadores que no leen SVG en el favicon,
- el **Apple touch icon** (180×180) para cuando alguien guarda tu sitio en la pantalla de inicio de iOS,
- el **web manifest** con sus íconos para apps instalables,
- y los posibles **fallbacks** para clientes antiguos.

## Una estrategia práctica

Para mis próximos proyectos, esto es lo que pienso aplicar según el caso.

**Opción simple** — un experimento, una demo, un side project:

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
```

**Opción más completa** — un sitio serio, un portafolio, algo instalable:

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
```

**Opción con fallback legacy** — si de verdad necesitas cubrir navegadores muy viejos:

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="shortcut icon" href="/favicon.ico" />
```

Nótese el orden: el navegador moderno toma el SVG; el que no puede, cae al PNG; y solo el realmente antiguo termina en el `.ico`.

¿Significa esto "nunca uses `.ico`"? No. Yo no lo pensaría como el protagonista, sino como el casco viejo que puedes guardar en el baúl si necesitas compatibilidad extra. Está ahí, funciona, y no molesta — pero ya no es lo primero que te pones.

## Cierre

El favicon es un detalle pequeño, pero los detalles pequeños revelan cómo pensamos una interfaz. Nadie va a elogiar tu favicon adaptable al modo oscuro; y sin embargo, la diferencia entre un sitio cuidado y uno improvisado se acumula precisamente en cosas así. Usar SVG no es solo modernizar un archivo: es aceptar que incluso las piezas más diminutas de una web pueden ser más limpias, adaptables y cuidadas.

## Checklist para mis próximos proyectos

- [ ] Crear un `favicon.svg` con el logo simplificado (formas limpias, legible a 16px).
- [ ] Añadir CSS interno con `@media (prefers-color-scheme: dark)` si el logo lo necesita.
- [ ] Declararlo con `<link rel="icon" type="image/svg+xml" href="/favicon.svg">`.
- [ ] Generar el paquete completo con [RealFaviconGenerator](https://realfavicongenerator.net/) si el proyecto es serio: PNGs, Apple touch icon, manifest.
- [ ] Añadir `favicon.ico` solo si la compatibilidad con navegadores viejos importa de verdad.
- [ ] Probar el resultado en modo claro y oscuro, en más de un navegador.
- [ ] Verificar que no queda el favicon por defecto del framework.
