# Gallinero tractor de Plastimadera — visor 3D / realidad aumentada

App web gratuita (sin instalar nada) para mostrar la propuesta de gallinero tractor móvil de madera plástica reciclada para Fundación Armadillo: gallinero (2 m) + corral modular (4 m), 2 módulos con ruedas removibles, techo 2 % con canaleta, nidos autocosechantes, perchas escalonadas, comederos PVC 3", bebederos de flotador y arpilla atrapanieblas.

- App (model-viewer, "Ver en mi espacio" a escala real): https://tortugadante.github.io/gallinero-tractor-ar/
- AR sobre imagen ancla (MindAR, apuntar al cartel): https://tortugadante.github.io/gallinero-tractor-ar/ar-ancla.html

Tecnología: model-viewer 4 (CDN), A-Frame 1.5 + MindAR 1.2.5 (CDN), GitHub Pages (HTTPS, necesario para cámara/AR). El workflow `.github/workflows/pages.yml` decodifica `targets/*.mind.b64` y publica en la rama `gh-pages`.

Estructura: `index.html`, `ar-ancla.html`, `gallinero_tractor.gltf`, `gallinero_explosivo.gltf`, `targets/`, `LICENSE`.

Estado: boceto de desarrollo; cotas nominales y largo comercial supuesto (2.44 m). No es plano de fabricación.
