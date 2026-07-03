---
title: "JavaScript sin punto y coma, pero con cuidado"
published: true
description: "Escribo JavaScript sin punto y coma y me funciona bien — porque conozco las excepciones. Qué es ASI, por qué una línea que empieza con ( o [ puede romper tu código, y el ; defensivo que lo evita."
tags: ["JavaScript", "Frontend", "Referencia"]
date: "Jul 3 2026"
---

Me gusta JavaScript. Y me gusta escribirlo sin punto y coma: el código se ve más limpio, más fluido, con menos ruido visual al final de cada línea. Pero no quiero que esa preferencia dependa de magia que no entiendo. Si voy a omitir el `;`, quiero saber exactamente *por qué* puedo hacerlo — y en qué casos el lenguaje me va a pasar factura.

Este artículo es mi guía personal para eso. No es un manifiesto de "nunca uses `;`" ni una guerra de estilos. La idea central es simple:

> **Puedes escribir JavaScript sin `;` y estar perfectamente bien, pero tienes que conocer las excepciones donde omitirlo rompe tu código.**

## ASI: por qué esto funciona

Empecemos por lo obvio. Este código no tiene un solo punto y coma y funciona perfecto:

```js
const name = 'Luis'
const language = 'JavaScript'

console.log(`${name} likes ${language}`)
```

Funciona gracias a **ASI** (*Automatic Semicolon Insertion*): un mecanismo definido en la propia especificación de ECMAScript. La gramática de JavaScript *sí* requiere punto y coma para terminar la mayoría de los statements — pero cuando el parser encuentra un token que no puede encajar en la instrucción actual y hay un salto de línea de por medio, inserta un `;` implícito y sigue adelante. También lo inserta al final del archivo y en unos pocos casos especiales que veremos más abajo.

El detalle importante está en la definición: ASI no es "JavaScript pone `;` al final de cada línea". Es más bien un mecanismo de *corrección de errores*: el parser solo inserta el punto y coma cuando **no puede** seguir interpretando la línea siguiente como continuación de la actual. Y ahí está la trampa — porque a veces sí puede.

### El contraste con Python

Vale la pena compararlo con Python, que también se escribe sin `;` pero por una razón completamente distinta. En Python, el salto de línea **forma parte de la gramática**: el lexer emite un token `NEWLINE` que termina el statement, y continuar una instrucción en la línea siguiente requiere algo explícito (paréntesis abiertos, corchetes, o un `\`). El punto y coma existe en Python, pero solo como separador opcional de statements en una misma línea, y el estilo idiomático nunca lo usa.

En JavaScript es al revés: el terminador oficial es el `;`, el salto de línea es (casi siempre) whitespace sin significado, y ASI es la capa de recuperación que hace que parezca que el newline termina la instrucción. Por eso en Python nunca piensas en esto y en JavaScript tienes que conocer las excepciones: **en Python el newline separa por diseño; en JavaScript separa solo cuando la gramática no tiene otra opción.**

## El problema real

Como ASI solo actúa cuando la línea siguiente *no puede* ser continuación de la anterior, el peligro aparece cuando una línea nueva empieza con un carácter que **sí** puede continuar la expresión previa. En ese caso el parser no inserta nada: une las dos líneas en una sola instrucción, sin avisarte.

Los sospechosos habituales son pocos, y casi siempre los mismos: `(`, `[` y el backtick de los template literals.

## El caso que me hizo escribir esto: una async IIFE

Este es el ejemplo que quiero dejar documentado. Parece inofensivo:

```js
Promise.resolve()

(async () => {
  console.log('Running async code')
})()
```

Para el parser, ese `(` de la segunda instrucción es una continuación perfectamente válida de la primera. Lo que JavaScript ve es esto:

```js
Promise.resolve()(async () => { ... })()
```

Es decir: llama a `Promise.resolve()`, y luego intenta **llamar al resultado como si fuera una función**, pasándole la arrow function como argumento. Una promesa no es invocable, así que en tiempo de ejecución explota:

```
TypeError: Promise.resolve(...) is not a function
```

Nota lo traicionero del asunto: no es un error de sintaxis. El código *parsea* sin problema y el error aparece en runtime, posiblemente lejos de donde lo escribiste. Ni siquiera la línea en blanco te salva — para ASI, uno o veinte saltos de línea dan igual.

La solución es un punto y coma **al inicio** de la línea peligrosa:

```js
Promise.resolve()

;(async () => {
  console.log('Running async code')
})()
```

Ese `;` corta explícitamente la instrucción anterior. Se le conoce como *defensive semicolon* o *leading semicolon*, y es la pieza clave de este estilo: no significa que ahora voy a usar punto y coma en todas partes. Es un `;` estratégico, colocado exactamente donde la gramática lo necesita — y como va pegado al inicio de la línea, además funciona como señal para quien lee: "ojo, esta línea empieza con un carácter que podría fusionarse con lo de arriba".

## Los otros casos donde conviene el `;` inicial

### Línea que empieza con `[`

```js
const numbers = [1, 2, 3]

;[4, 5, 6].forEach(number => {
  console.log(number)
})
```

Sin el `;`, JavaScript interpreta `[4, 5, 6]` como un acceso por índice sobre la línea anterior: `numbers[4, 5, 6]` (donde `4, 5, 6` es el operador coma y evalúa a `6`). Otra vez: parsea bien, falla en runtime — o peor, no falla y hace algo que no querías.

### Línea que empieza con `(` (la IIFE clásica)

```js
const message = 'Hello'

;(function () {
  console.log(message)
})()
```

El mismo patrón que la async IIFE: sin el `;`, el `(` intentaría invocar lo que haya quedado a la izquierda.

### Línea que empieza con un template literal

```js
const name = getName()

;`${name} escribe JavaScript`.split(' ')
```

Sin el `;`, el backtick convierte la expresión anterior en un *tagged template*: `getName()`&#96;...&#96; — es decir, intenta usar el resultado de `getName()` como función de tag. Es un caso más raro en código real, pero existe y sigue la misma lógica.

### Menciones honorables

Hay otros caracteres que en teoría pueden fusionar líneas: `/` (que puede leerse como división), `+` y `-` (operadores binarios). En la práctica casi nunca escribes una línea que empiece con ellos, así que no vale la pena obsesionarse. Si algún día lo haces, ya sabes la regla: `;` al frente y a otra cosa.

## Mi regla personal

Esto es lo que aplico, y lo que quiero recordar cada vez que vuelva aquí:

- **No** uso `;` al final de cada statement.
- **Sí** uso `;` al inicio de cualquier línea que empiece con `(`, `[` o `` ` ``.
- Especialmente si estoy escribiendo una IIFE o una async IIFE, que es donde este patrón aparece de verdad.
- No es una cuestión de estética solamente: es conocer la gramática del lenguaje en el que trabajo.

En la práctica, las líneas que empiezan con esos caracteres son raras — por eso el estilo sin `;` es viable. Pero cuando aparecen, aparecen en serio.

## Prettier, ESLint y el mundo real

Si usas Prettier, por defecto **añade** punto y coma en todas partes. Para el estilo sin `;`, basta con configurarlo:

```json
{
  "semi": false
}
```

Con esa opción, Prettier no solo quita los `;` finales: también **añade automáticamente el `;` defensivo** en las líneas que lo necesitan. Es la mejor razón para usar un formateador — la regla que describe este artículo deja de depender de tu memoria. En ESLint, el equivalente es la regla de estilo `semi` con `"never"` (hoy vía `@stylistic`), acompañada de `no-unexpected-multiline`, que detecta justo las fusiones de línea peligrosas.

Y una aclaración importante: en proyectos reales, lo primero es la convención del equipo. Si el proyecto usa `;`, usa `;` — no es una batalla que valga la pena dar en un pull request. Si el proyecto no los usa, entonces sí: apréndete las excepciones, porque son parte del trato.

## Bonus: el `return` traicionero (esto no lo arregla un `;` defensivo)

ASI tiene otra cara que conviene conocer, aunque sea un problema distinto. Hay unos pocos lugares donde la gramática **prohíbe** el salto de línea — las llamadas *restricted productions* — y ahí ASI hace lo contrario de lo que vimos: inserta un `;` aunque tú no quieras. El caso clásico es `return`:

```js
return
{
  ok: true
}
```

Esto **no** devuelve el objeto. ASI inserta un `;` inmediatamente después de `return`, así que la función devuelve `undefined`, y el bloque de abajo queda como código muerto. La solución es no dejar solo al `return`:

```js
return {
  ok: true
}
```

Fíjate que aquí el `;` defensivo no pinta nada — el problema no es una línea que continúa la anterior, sino un salto de línea donde el lenguaje no lo tolera. Lo mismo aplica a `throw`, `break`, `continue` y a los operadores `++`/`--`. Lo menciono porque refuerza el punto central del artículo: el tema nunca fue "semicolons sí o no", sino **entender qué hace ASI**.

## Conclusión

No usar `;` está bien. Usar `;` también está bien. Lo único genuinamente peligroso es escribir JavaScript sin saber cuándo el parser va a interpretar tu línea nueva como continuación de la anterior — eso te puede morder con cualquiera de los dos estilos.

Mi postura, para dejarla escrita: **JavaScript sin punto y coma, pero no sin criterio.**

## TL;DR

- ASI permite omitir `;` porque el parser los inserta cuando la línea siguiente *no puede* continuar la expresión anterior.
- El peligro: líneas que empiezan con `(`, `[` o `` ` `` — esas **sí** pueden continuar la expresión anterior, y ASI no interviene.
- La solución: un `;` defensivo al **inicio** de esas líneas: `;(async () => { ... })()`.
- El caso estrella: una IIFE (normal o async) después de cualquier expresión.
- `return` + salto de línea + objeto devuelve `undefined`. Eso es otra cara de ASI y se arregla abriendo la llave en la misma línea.
- Prettier con `"semi": false` aplica todo esto por ti. ESLint: `semi: "never"` + `no-unexpected-multiline`.
- En equipo, manda la convención del proyecto.
- Python no tiene este problema porque su gramática termina statements en el newline; JavaScript los termina en `;` y ASI solo es la red de seguridad.
