---
title: "Markdown Style Guide"
published: true
description: "Una muestra de la sintaxis básica de Markdown que uso al escribir contenido en este sitio. Sirve de referencia visual para la tipografía del blog."
tags: ["Markdown", "Referencia"]
date: "Jul 3 2026"
---

Este post es una referencia visual: recorre la sintaxis básica de Markdown para ver cómo se renderiza cada elemento con los estilos del sitio. Si algo se ve raro aquí, se va a ver raro en todos los posts.

## Encabezados

Los encabezados van de `#` (h1) a `######` (h6). En los posts, el h1 lo pone el título del frontmatter, así que el contenido empieza en h2.

### Esto es un h3

#### Esto es un h4

##### Esto es un h5

## Párrafos y énfasis

Un párrafo normal se escribe tal cual, sin nada especial. Markdown junta las líneas consecutivas en un solo párrafo, y una línea en blanco separa párrafos.

El texto puede llevar **negritas** con dos asteriscos, *itálicas* con uno, y ***ambas*** con tres. También hay ~~tachado~~ con virgulillas dobles, y `código inline` con backticks.

## Enlaces

Un [enlace básico](https://astro.build) se escribe con corchetes y paréntesis. También funcionan los enlaces con título: [Tailwind CSS](https://tailwindcss.com "Documentación de Tailwind").

## Citas

> Esto es una cita en bloque. Útil para destacar una idea de otra fuente o un aviso importante.
>
> Puede tener varios párrafos si cada línea empieza con `>`.

## Listas

Lista sin orden:

- Primer elemento
- Segundo elemento
  - Elemento anidado
  - Otro anidado
- Tercer elemento

Lista ordenada:

1. Instalar dependencias
2. Configurar el proyecto
3. Escribir contenido
4. Publicar

## Código

Bloque de código con resaltado de sintaxis (se indica el lenguaje después de los tres backticks):

```js
export function saludo(nombre) {
  return `Hola, ${nombre}`;
}
```

```css
.tarjeta {
  border-radius: 0.5rem;
  padding: 1rem;
}
```

Y un bloque sin lenguaje:

```
texto plano, sin resaltado
```

## Tablas

| Elemento | Sintaxis | Ejemplo |
|---|---|---|
| Negritas | `**texto**` | **texto** |
| Itálicas | `*texto*` | *texto* |
| Código | `` `texto` `` | `texto` |
| Enlace | `[texto](url)` | [texto](#tablas) |

## Imágenes

La sintaxis es como la de un enlace, con `!` al frente:

```md
![Texto alternativo](/ruta/a/la/imagen.png)
```

## Línea horizontal

Tres guiones en una línea sola generan un separador:

---

Y eso es todo. Si añado estilos nuevos a la tipografía del sitio, este post es el primero que reviso.
