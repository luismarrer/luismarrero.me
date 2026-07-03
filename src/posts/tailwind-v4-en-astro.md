---
title: "Tailwind CSS v4 en Astro: adiós al config.js automático, hola a global.css y astro.config.mjs"
published: true
description: "Guía rápida para usar Tailwind CSS v4 en Astro: el nuevo enfoque CSS-first, el plugin de Vite, @theme, @source, y qué pasa con tailwind.config.js."
tags: ["Tailwind", "Astro", "CSS"]
date: "Jul 3 2026"
---

Esto lo escribo para mi yo del futuro, que en seis meses va a montar otro proyecto con Astro y va a buscar en Google "cómo configurar Tailwind" y se va a topar con veinte tutoriales viejos que empiezan con `npx tailwindcss init`. No, yo del futuro: eso era Tailwind v3. Las cosas cambiaron.

Tailwind CSS v4 cambia la forma de configurar proyectos. Antes era normal crear (o depender de) un `tailwind.config.js` como el centro de todo: ahí vivía el tema, el `content`, los plugins, el `safelist`... todo. En v4 la configuración principal se mueve al CSS. El archivo `tailwind.config.js` **ya no se detecta automáticamente** — todavía se puede usar por compatibilidad, pero hay que cargarlo explícitamente.

Este artículo es la guía rápida que me hubiese gustado tener: cómo instalar y configurar Tailwind v4 en Astro, y qué cambió de mentalidad respecto a v3.

## Qué cambió en Tailwind v4

Lo primero que notas al abrir un proyecto v4 es el CSS. Ya no se usan las tres directivas clásicas:

```css
/* Esto era Tailwind v3 — ya no */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

En v4 todo eso se reemplaza con una sola línea:

```css
@import "tailwindcss";
```

Y a partir de ahí, la configuración es *CSS-first*, con directivas nuevas que viven en tu hoja de estilos:

- `@theme` — para definir tokens de diseño (colores, fuentes, espaciados) como variables CSS.
- `@source` — para indicarle a Tailwind fuentes de contenido que no detecta solo.
- `@config` — para cargar un `tailwind.config.js` explícitamente, si lo necesitas.

Sobre ese último punto, que es donde más se confunde la gente: `tailwind.config.js` **sigue siendo soportado** por compatibilidad, pero Tailwind v4 no lo va a buscar automáticamente en la raíz del proyecto como hacía v3. Si quieres usarlo, tienes que declararlo tú en el CSS:

```css
@import "tailwindcss";
@config "../../tailwind.config.js";
```

Además, aunque cargues un config JS, no todo lo de v3 funciona: opciones como `corePlugins`, `safelist` y `separator` **ya no son soportadas** desde el config en v4. Para safelisting, la forma nueva es `@source inline()` (más abajo hay un ejemplo).

## Cómo instalar Tailwind v4 en Astro

El enfoque moderno recomendado es el plugin oficial de Vite:

```sh
pnpm add tailwindcss @tailwindcss/vite
```

O, si tu versión de Astro es reciente, puedes dejar que Astro lo haga por ti:

```sh
pnpm astro add tailwind
```

Ese comando instala las dependencias y configura el plugin de Vite automáticamente. Ojo: en versiones modernas de Astro, `astro add tailwind` ya configura Tailwind v4 con `@tailwindcss/vite`, **no** la integración vieja `@astrojs/tailwind`, que era la forma de hacerlo en la era de Tailwind v3.

## Configuración en `astro.config.mjs`

Astro usa Vite por debajo, y Tailwind v4 recomienda usar el plugin `@tailwindcss/vite`. Así que la configuración en Astro es registrar el plugin en la sección `vite`:

```js
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
});
```

Esto reemplaza el enfoque viejo de depender de `@astrojs/tailwind`. Esa integración era el estándar con Tailwind v3, pero para v4 el camino es el plugin de Vite directo.

> Nota secundaria: también existe `@tailwindcss/postcss` si por alguna razón necesitas Tailwind como plugin de PostCSS, pero en Astro no hay motivo para complicarse — el plugin de Vite es más simple y es lo recomendado.

## Configuración en `src/styles/global.css`

Con el plugin registrado, `global.css` se vuelve el lugar principal donde se importa Tailwind. Lo mínimo es esto:

```css
@import "tailwindcss";
```

Y ya. Con eso tienes todas las utilidades disponibles. Pero aquí es donde brilla el enfoque CSS-first: en este mismo archivo defines tus tokens de diseño con `@theme`:

```css
@import "tailwindcss";

@theme {
  --color-brand: #0ea5e9;
  --font-sans: "Inter", sans-serif;
}
```

Los tokens definidos como variables CSS dentro de `@theme` se convierten en utilidades de Tailwind según su namespace: `--color-brand` genera clases como `bg-brand`, `text-brand` o `border-brand`, y `--font-sans` alimenta la utilidad `font-sans`. O sea, lo que antes hacías en `theme.extend` del config JS, ahora lo haces en CSS puro, con variables que además puedes usar directamente en cualquier regla CSS tuya.

## Cómo importar `global.css` en Astro

En Astro lo normal es importar el CSS global desde un layout compartido, para que las clases de Tailwind estén disponibles en todas las páginas que usen ese layout:

```astro
---
import "../styles/global.css";
---

<html lang="es">
  <head>
    <meta charset="utf-8" />
    <title>Astro + Tailwind v4</title>
  </head>
  <body>
    <slot />
  </body>
</html>
```

Evita el `<link rel="stylesheet" href="/src/styles/global.css" />` a mano — el import en el frontmatter deja que Vite procese el archivo (que es justo lo que Tailwind necesita) y Astro se encarga del resto.

## ¿Qué pasa con `@source`?

En Tailwind v3, el config tenía un `content: []` obligatorio donde listabas todos los archivos donde usabas clases. En v4 hay **detección automática de contenido** en muchos casos: Tailwind escanea tu proyecto solo, ignorando cosas como `node_modules`, archivos binarios y lo que esté en `.gitignore`. Por eso ya no siempre hace falta declarar nada.

`@source` no es un reemplazo obligatorio de `content` — es una herramienta para cuando Tailwind **no detecta algo automáticamente**. Casos típicos:

- Una librería interna en `node_modules` (que Tailwind ignora por defecto).
- Archivos fuera del árbol esperado del proyecto.
- Clases generadas dinámicamente que nunca aparecen escritas completas en el código.

```css
@import "tailwindcss";
@source "../node_modules/@mi-org/ui-lib";
```

Y para safelisting — clases que quieres forzar en el build aunque no aparezcan en ningún archivo — se usa `@source inline()`:

```css
@source inline("bg-red-500 text-center hover:bg-blue-500");
```

Esto sustituye al `safelist` del config JS, que como mencioné arriba ya no es soportado en v4.

## ¿Cuándo todavía usar `tailwind.config.js`?

Hay casos legítimos:

- **Migración desde v3**: tienes un proyecto viejo con un config grande y no quieres mover todo al CSS de un cantazo.
- **Plugins o lógica JS**: configuración que genera valores programáticamente y que todavía no quieres reescribir.
- **Monorepos**: una configuración compartida entre varios proyectos que vive en un paquete JS.

Pero repito lo importante, porque es el error #1 al migrar: **en v4 el archivo no se detecta automáticamente**. Tienes que cargarlo tú en `global.css`:

```css
@import "tailwindcss";
@config "../../tailwind.config.js";
```

(La ruta es relativa al archivo CSS, así que ajústala según dónde viva tu `global.css`.)

## Tabla comparativa: v3 vs v4

| Tailwind v3 | Tailwind v4 |
|---|---|
| `tailwind.config.js` era central | Configuración CSS-first |
| `content: []` en el config | Detección automática + `@source` cuando hace falta |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| `safelist` en el config | `@source inline()` |
| Integración Astro con `@astrojs/tailwind` | Tailwind v4 con `@tailwindcss/vite` |

## Mini ejemplo final

Un proyecto Astro + Tailwind v4 mínimo y funcional, en cuatro archivos:

**`astro.config.mjs`**

```js
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
});
```

**`src/styles/global.css`**

```css
@import "tailwindcss";

@theme {
  --color-brand: #0ea5e9;
  --font-sans: "Inter", sans-serif;
}
```

**`src/layouts/Layout.astro`**

```astro
---
import "../styles/global.css";
---

<html lang="es">
  <head>
    <meta charset="utf-8" />
    <title>Astro + Tailwind v4</title>
  </head>
  <body class="bg-slate-50 font-sans">
    <slot />
  </body>
</html>
```

**`src/pages/index.astro`**

```astro
---
import Layout from "../layouts/Layout.astro";
---

<Layout>
  <main class="mx-auto max-w-2xl p-8">
    <h1 class="text-3xl font-bold text-brand">Hola, Tailwind v4</h1>
    <p class="mt-4 text-slate-700">
      Sin <code class="rounded bg-slate-200 px-1">tailwind.config.js</code> y
      sin remordimientos.
    </p>
  </main>
</Layout>
```

Fíjate en el `text-brand`: esa clase existe porque definimos `--color-brand` en `@theme`. Ningún config JS involucrado.

## Cierre

Tailwind v4 no elimina totalmente `tailwind.config.js`, pero deja de hacerlo el centro del proyecto. En Astro, la configuración moderna se divide en dos lugares claros:

- **`astro.config.mjs`** — registrar el plugin `@tailwindcss/vite`.
- **`src/styles/global.css`** — importar Tailwind y definir tema, fuentes y tokens con `@theme`.

La idea principal: menos configuración JS, más CSS explícito. Y si te encuentras un tutorial que empieza creando un `tailwind.config.js` con `content: []`, ya sabes que estás leyendo una guía de v3.
