/* ============================================================
   CÁTEDRA DE LA HISPANIDAD — Datos del sitio
   Contenido DEMOSTRATIVO y editable. En WordPress estos datos
   provendrán de los CPT (proyectos, actividades, publicaciones…)
   vía wp_localize_script o de la REST API.
   ============================================================ */

/* Navegación principal (alimenta mega menú, menú móvil y palette) */
window.CH_NAV = [
  {
    label: "La Cátedra", url: "la-catedra.html",
    feature: { img: "assets/img/estudiantes.png", kicker: "Presentación", title: "Una conversación académica entre orillas", url: "la-catedra.html" },
    items: [
      ["Quiénes somos", "la-catedra.html#quienes-somos"],
      ["Campo de estudio", "la-catedra.html#campo-de-estudio"],
      ["Misión y valores", "la-catedra.html#mision"],
      ["Qué pretendemos", "la-catedra.html#que-pretendemos"],
      ["Historia", "la-catedra.html#historia"],
      ["Dirección y equipo", "equipo.html"],
      ["Instituciones impulsoras", "la-catedra.html#instituciones"],
      ["Contacto institucional", "contacto.html"]
    ]
  },
  {
    label: "Investigación", url: "investigacion.html",
    feature: { img: "assets/img/libro2.png", kicker: "Proyecto activo", title: "Redes jurídicas e instituciones del mundo hispánico", url: "proyecto.html" },
    items: [
      ["Presentación", "investigacion.html"],
      ["Áreas temáticas", "investigacion.html#areas"],
      ["Líneas de investigación", "investigacion.html#lineas"],
      ["Proyectos activos", "proyectos.html?estado=activo"],
      ["Proyectos finalizados", "proyectos.html?estado=finalizado"],
      ["Todos los proyectos", "proyectos.html"],
      ["Investigadores", "equipo.html#investigadores"],
      ["Resultados y publicaciones", "repositorio.html"]
    ]
  },
  {
    label: "Actividades", url: "actividades.html",
    feature: { img: "assets/img/aulas.png", kicker: "Próximamente", title: "Seminario permanente: Pensar la Hispanidad en el siglo XXI", url: "actividad.html" },
    items: [
      ["Agenda general", "actividades.html"],
      ["Próximas actividades", "actividades.html#proximas"],
      ["Seminarios permanentes", "actividades.html?tipo=seminario"],
      ["Cursos de verano", "actividades.html?tipo=curso"],
      ["Congresos y jornadas", "actividades.html?tipo=jornada"],
      ["Conferencias", "actividades.html?tipo=conferencia"],
      ["Actividades celebradas", "actividades.html#celebradas"],
      ["Vista de calendario", "actividades.html#calendario"]
    ]
  },
  {
    label: "Publicaciones", url: "publicaciones.html",
    feature: { img: "assets/img/libro3.jpg", kicker: "Revista", title: "Cuadernos de la Hispanidad · N.º 1", url: "revista-numero-01.html" },
    items: [
      ["Panorama de publicaciones", "publicaciones.html"],
      ["Revista de la Cátedra", "revista.html"],
      ["Último número", "revista-numero-01.html"],
      ["Repositorio de libre acceso", "repositorio.html"],
      ["Documentos de trabajo", "repositorio.html?tipo=documento"],
      ["Convocatoria editorial", "publicaciones.html#convocatoria"],
      ["Normas para autores", "publicaciones.html#normas"],
      ["Comité editorial", "publicaciones.html#comite"]
    ]
  },
  {
    label: "Multimedia", url: "multimedia.html",
    feature: { img: "assets/img/conquista.png", kicker: "Archivo audiovisual", title: "La Hispanidad: memoria visual comentada", url: "multimedia.html" },
    items: [
      ["Galería multimedia", "multimedia.html"],
      ["Fotografías", "multimedia.html?tipo=foto"],
      ["Vídeos", "multimedia.html?tipo=video"],
      ["Conferencias grabadas", "multimedia.html?tipo=conferencia"],
      ["Documentos gráficos", "multimedia.html?tipo=documento"]
    ]
  },
  {
    label: "Más", url: "premios.html",
    feature: { img: "assets/img/libro5.jpg", kicker: "Convocatoria", title: "Premio de Ensayo de la Cátedra · 1.ª edición", url: "premios.html" },
    items: [
      ["Premios y convocatorias", "premios.html"],
      ["Bases y documentación", "premios.html#bases"],
      ["Convenios y colaboraciones", "convenios.html"],
      ["Prensa", "contacto.html#prensa"],
      ["Contacto", "contacto.html"],
      ["Aviso legal", "aviso-legal.html"],
      ["Privacidad", "privacidad.html"],
      ["Accesibilidad", "accesibilidad.html"]
    ]
  }
];

/* Índice de búsqueda global.
   type: persona | proyecto | area | actividad | revista | publicacion | multimedia | premio | convenio | pagina */
window.CH_INDEX = [
  // Páginas
  { t: "Quiénes somos", type: "pagina", url: "la-catedra.html", d: "Presentación, misión, campo de estudio e historia de la Cátedra." },
  { t: "Dirección y equipo", type: "pagina", url: "equipo.html", d: "Dirección, coordinación, consejo académico, docentes, investigadores y colaboradores." },
  { t: "Contacto y colaboraciones", type: "pagina", url: "contacto.html", d: "Datos institucionales, formulario y propuesta de colaboración." },
  { t: "Repositorio de libre acceso", type: "pagina", url: "repositorio.html", d: "Artículos, informes, documentos de trabajo y monografías en abierto." },
  { t: "Agenda de actividades", type: "pagina", url: "actividades.html", d: "Seminarios, cursos de verano, congresos, jornadas y conferencias." },
  { t: "Convenios y red de colaboración", type: "pagina", url: "convenios.html", d: "Universidades, empresas e instituciones colaboradoras." },
  { t: "Premios y convocatorias", type: "pagina", url: "premios.html", d: "Convocatorias abiertas, bases y ganadores de ediciones anteriores." },

  // Áreas temáticas
  { t: "Historia, memoria y patrimonio", type: "area", url: "investigacion.html#area-1", d: "Procesos históricos, memorias compartidas y patrimonio material e inmaterial." },
  { t: "Lenguas, literatura y pensamiento", type: "area", url: "investigacion.html#area-2", d: "El español y las lenguas del mundo hispánico, creación literaria e historia intelectual." },
  { t: "Derecho e instituciones", type: "area", url: "investigacion.html#area-3", d: "Tradiciones jurídicas, instituciones y culturas político-administrativas." },
  { t: "Arte y cultura visual", type: "area", url: "investigacion.html#area-4", d: "Artes plásticas, arquitectura, imagen y circulación de modelos estéticos." },
  { t: "Sociedad, movilidad y diásporas", type: "area", url: "investigacion.html#area-5", d: "Migraciones, comunidades transnacionales y transformación social." },
  { t: "Relaciones transatlánticas", type: "area", url: "investigacion.html#area-6", d: "Vínculos políticos, económicos y culturales entre Europa y América." },
  { t: "Educación y transmisión cultural", type: "area", url: "investigacion.html#area-7", d: "Sistemas educativos, enseñanza del español y divulgación del conocimiento." },
  { t: "Economía, ciencia y redes de conocimiento", type: "area", url: "investigacion.html#area-8", d: "Intercambios económicos y científicos en el espacio hispánico." },

  // Proyectos (demostrativos)
  { t: "Redes jurídicas e instituciones del mundo hispánico", type: "proyecto", url: "proyecto.html", d: "Proyecto demostrativo · Activo · Derecho e instituciones." },
  { t: "Memoria, patrimonio y circulación cultural", type: "proyecto", url: "proyectos.html", d: "Proyecto demostrativo · Activo · Historia, memoria y patrimonio." },
  { t: "Lengua, pensamiento y creación entre orillas", type: "proyecto", url: "proyectos.html", d: "Proyecto demostrativo · Activo · Lenguas, literatura y pensamiento." },
  { t: "Movilidad, migraciones y comunidades transatlánticas", type: "proyecto", url: "proyectos.html", d: "Proyecto demostrativo · Finalizado · Sociedad, movilidad y diásporas." },

  // Actividades (demostrativas)
  { t: "Seminario permanente: Pensar la Hispanidad en el siglo XXI", type: "actividad", url: "actividad.html", d: "Sesión inaugural del curso 2026–2027. Modalidad híbrida." },
  { t: "Jornada: Archivos, memoria y patrimonio compartido", type: "actividad", url: "actividades.html", d: "Jornada académica con mesas redondas y visita a archivo." },
  { t: "Curso de verano: Historia, cultura e instituciones del mundo hispánico", type: "actividad", url: "actividades.html", d: "Curso intensivo presencial con matrícula abierta." },
  { t: "Conversación pública: Lengua, identidad y transformación social", type: "actividad", url: "actividades.html", d: "Diálogo abierto al público general. Entrada libre." },

  // Revista y publicaciones (demostrativas)
  { t: "Cuadernos de la Hispanidad · N.º 1", type: "revista", url: "revista-numero-01.html", d: "Número inaugural de la revista de la Cátedra. Monográfico demostrativo." },
  { t: "Revista de la Cátedra", type: "revista", url: "revista.html", d: "Portada de la revista: números, normas, comité y convocatoria." },
  { t: "La Hispanidad como problema historiográfico", type: "publicacion", url: "publicacion.html", d: "Artículo demostrativo · Acceso abierto · PDF descargable." },
  { t: "Documento de trabajo: Cartografías del español contemporáneo", type: "publicacion", url: "repositorio.html", d: "Documento de trabajo demostrativo en acceso abierto." },
  { t: "Informe: Instituciones y cultura jurídica hispánica", type: "publicacion", url: "repositorio.html", d: "Informe demostrativo vinculado al proyecto de redes jurídicas." },
  { t: "Defensa de la Hispanidad (fondo bibliográfico)", type: "publicacion", url: "repositorio.html", d: "Referencia del fondo bibliográfico histórico de la Cátedra." },

  // Multimedia
  { t: "Galería multimedia", type: "multimedia", url: "multimedia.html", d: "Fotografías, vídeos, entrevistas y documentos gráficos." },
  { t: "Vídeo: La Hispanidad — memoria visual comentada", type: "multimedia", url: "multimedia.html", d: "Pieza audiovisual de presentación de la Cátedra." },

  // Premios / convenios
  { t: "Premio de Ensayo de la Cátedra · 1.ª edición", type: "premio", url: "premios.html", d: "Convocatoria demostrativa abierta. Consulta las bases y plazos." },
  { t: "Universidad Rey Juan Carlos (institución impulsora)", type: "convenio", url: "convenios.html", d: "Institución responsable de la Cátedra." },

  // Personas (fichas demostrativas, sin nombres reales)
  { t: "Dirección de la Cátedra (perfil editable)", type: "persona", url: "persona.html", d: "Ficha demostrativa de la dirección académica. Sustituir desde el CMS." },
  { t: "Coordinación académica (perfil editable)", type: "persona", url: "equipo.html", d: "Ficha demostrativa de coordinación. Sustituir desde el CMS." },
  { t: "Investigadores de la Cátedra", type: "persona", url: "equipo.html#investigadores", d: "Listado de perfiles de investigación vinculados." }
];

/* Actividades para agenda y calendario (fechas demostrativas) */
window.CH_EVENTS = [
  { date: "2026-09-24", time: "17:00–19:00", title: "Seminario permanente: Pensar la Hispanidad en el siglo XXI", type: "Seminario", mode: "Híbrida", place: "Campus universitario · Aula por confirmar", url: "actividad.html" },
  { date: "2026-10-08", time: "10:00–14:00", title: "Jornada: Archivos, memoria y patrimonio compartido", type: "Jornada", mode: "Presencial", place: "Biblioteca central", url: "actividades.html" },
  { date: "2026-10-22", time: "18:00–19:30", title: "Conversación pública: Lengua, identidad y transformación social", type: "Conversación", mode: "Presencial", place: "Salón de actos", url: "actividades.html" },
  { date: "2026-11-12", time: "17:00–19:00", title: "Seminario permanente · Sesión 2: Atlas y archivos digitales", type: "Seminario", mode: "Online", place: "Aula virtual", url: "actividades.html" },
  { date: "2027-07-05", time: "09:30–14:00", title: "Curso de verano: Historia, cultura e instituciones del mundo hispánico", type: "Curso", mode: "Presencial", place: "Sede de cursos de verano", url: "actividades.html" }
];

/* Sugerencias iniciales del buscador */
window.CH_SUGGESTIONS = [
  { t: "Proyectos activos", url: "proyectos.html?estado=activo", k: "Investigación" },
  { t: "Próximos seminarios", url: "actividades.html#proximas", k: "Actividades" },
  { t: "Último número de la revista", url: "revista-numero-01.html", k: "Revista" },
  { t: "Dirección y equipo", url: "equipo.html", k: "Personas" },
  { t: "Publicaciones en abierto", url: "repositorio.html", k: "Repositorio" }
];
