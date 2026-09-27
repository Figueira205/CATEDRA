/* ============================================================
   CÁTEDRA DE LA HISPANIDAD — Site data (English)
   DEMO / editable content. Mirrors data.js; keep both in sync.
   In WordPress this would come from the CPTs via wp_localize_script
   or the REST API.
   ============================================================ */

/* Main navigation (feeds the mega menu, mobile menu and palette) */
window.CH_NAV = [
  {
    label: "The Chair", url: "la-catedra.html",
    feature: { img: "../assets/img/estudiantes.png", kicker: "About", title: "An academic conversation across shores", url: "la-catedra.html" },
    items: [
      ["Who we are", "la-catedra.html#quienes-somos"],
      ["Mission and objectives", "la-catedra.html#mision"],
      ["Leadership and team", "equipo.html"],
      ["Research", "investigacion.html"],
      ["Projects", "proyectos.html"],
      ["Agreements and institutions", "convenios.html"]
    ]
  },
  {
    label: "Activities", url: "actividades.html",
    feature: { img: "../assets/img/aulas.png", kicker: "Coming up", title: "Ongoing seminar: Rethinking Hispanidad in the 21st Century", url: "actividad.html" },
    items: [
      ["Calendar", "actividades.html"],
      ["Upcoming activities", "actividades.html#proximas"],
      ["Calendar view", "actividades.html#calendario"],
      ["Past activities", "actividades.html#celebradas"],
      ["Prizes and calls", "premios.html"]
    ]
  },
  {
    label: "Library", url: "publicaciones.html",
    feature: { img: "../assets/img/libro3.jpg", kicker: "Journal", title: "Cuadernos de la Hispanidad · No. 1", url: "revista-numero-01.html" },
    items: [
      ["Full catalogue", "publicaciones.html"],
      ["Journal of the Chair", "revista.html"],
      ["Latest issue", "revista-numero-01.html"],
      ["Open-access publications", "repositorio.html"],
      ["Publish with us", "publicaciones.html#convocatoria"]
    ]
  },
  {
    label: "Gallery", url: "multimedia.html",
    feature: { img: "../assets/img/conquista.png", kicker: "Gallery", title: "Photographs and archival documents", url: "multimedia.html" },
    items: [
      ["Full gallery", "multimedia.html"],
      ["Photographs", "multimedia.html?tipo=foto"],
      ["Archival documents", "multimedia.html?tipo=documento"]
    ]
  },
  /* No «items»: shown as a direct link, no dropdown */
  { label: "Contact", url: "contacto.html" }
];

/* Global search index.
   type: persona | proyecto | area | actividad | revista | publicacion | multimedia | premio | convenio | pagina */
window.CH_INDEX = [
  // Pages
  { t: "Who we are", type: "pagina", url: "la-catedra.html", d: "Introduction, mission, field of study and history of the Chair." },
  { t: "Leadership and team", type: "pagina", url: "equipo.html", d: "Leadership, coordination, academic board, teaching staff, researchers and collaborators." },
  { t: "Contact and collaborations", type: "pagina", url: "contacto.html", d: "Institutional details, contact form and collaboration proposals." },
  { t: "Open-access repository", type: "pagina", url: "repositorio.html", d: "Open articles, reports, working papers and monographs." },
  { t: "Activities calendar", type: "pagina", url: "actividades.html", d: "Seminars, summer courses, conferences, workshops and talks." },
  { t: "Agreements and partner network", type: "pagina", url: "convenios.html", d: "Partner universities, companies and institutions." },
  { t: "Prizes and calls", type: "pagina", url: "premios.html", d: "Open calls, rules and winners of previous editions." },

  // Thematic areas
  { t: "History, memory and heritage", type: "area", url: "investigacion.html#area-1", d: "Historical processes, shared memories, and tangible and intangible heritage." },
  { t: "Languages, literature and thought", type: "area", url: "investigacion.html#area-2", d: "Spanish and the languages of the Hispanic world, literary creation and intellectual history." },
  { t: "Law and institutions", type: "area", url: "investigacion.html#area-3", d: "Legal traditions, institutions and political-administrative cultures." },
  { t: "Art and visual culture", type: "area", url: "investigacion.html#area-4", d: "Visual arts, architecture, imagery and the circulation of aesthetic models." },
  { t: "Society, mobility and diasporas", type: "area", url: "investigacion.html#area-5", d: "Migrations, transnational communities and social change." },
  { t: "Transatlantic relations", type: "area", url: "investigacion.html#area-6", d: "Political, economic and cultural ties between Europe and the Americas." },
  { t: "Education and cultural transmission", type: "area", url: "investigacion.html#area-7", d: "Education systems, the teaching of Spanish and the dissemination of knowledge." },
  { t: "Economy, science and knowledge networks", type: "area", url: "investigacion.html#area-8", d: "Economic and scientific exchange across the Hispanic world." },

  // Projects (demo)
  { t: "Legal networks and institutions of the Hispanic world", type: "proyecto", url: "proyecto.html", d: "Demo project · Active · Law and institutions." },
  { t: "Memory, heritage and cultural circulation", type: "proyecto", url: "proyectos.html", d: "Demo project · Active · History, memory and heritage." },
  { t: "Language, thought and creation across shores", type: "proyecto", url: "proyectos.html", d: "Demo project · Active · Languages, literature and thought." },
  { t: "Mobility, migrations and transatlantic communities", type: "proyecto", url: "proyectos.html", d: "Demo project · Completed · Society, mobility and diasporas." },

  // Activities (demo)
  { t: "Ongoing seminar: Rethinking Hispanidad in the 21st Century", type: "actividad", url: "actividad.html", d: "Opening session of the 2026–2027 term. Hybrid format." },
  { t: "Workshop: Archives, memory and shared heritage", type: "actividad", url: "actividades.html", d: "Academic workshop with panel discussions and an archive visit." },
  { t: "Summer course: History, culture and institutions of the Hispanic world", type: "actividad", url: "actividades.html", d: "Intensive in-person course, open enrolment." },
  { t: "Public conversation: Language, identity and social change", type: "actividad", url: "actividades.html", d: "Open to the general public. Free admission." },

  // Journal and publications (demo)
  { t: "Cuadernos de la Hispanidad · No. 1", type: "revista", url: "revista-numero-01.html", d: "Inaugural issue of the Chair's journal. Demo special issue." },
  { t: "Journal of the Chair", type: "revista", url: "revista.html", d: "Journal homepage: issues, guidelines, editorial board and call for papers." },
  { t: "Hispanidad as a historiographical problem", type: "publicacion", url: "publicacion.html", d: "Demo article · Open access · Downloadable PDF." },
  { t: "Working paper: Mapping contemporary Spanish", type: "publicacion", url: "repositorio.html", d: "Demo open-access working paper." },
  { t: "Report: Institutions and Hispanic legal culture", type: "publicacion", url: "repositorio.html", d: "Demo report linked to the legal networks project." },
  { t: "In Defense of Hispanidad (bibliographic collection)", type: "publicacion", url: "repositorio.html", d: "Reference from the Chair's historical bibliographic collection." },

  // Multimedia
  { t: "Gallery", type: "multimedia", url: "multimedia.html", d: "Photographs and archival documents." },

  // Prizes / agreements
  { t: "Chair Essay Prize · 1st edition", type: "premio", url: "premios.html", d: "Open demo call. Check the rules and deadlines." },
  { t: "Universidad Rey Juan Carlos (founding institution)", type: "convenio", url: "convenios.html", d: "Institution responsible for the Chair." },

  // People (demo profiles, no real names)
  { t: "Chair leadership (editable profile)", type: "persona", url: "persona.html", d: "Demo profile for the academic leadership. Replace via the CMS." },
  { t: "Academic coordination (editable profile)", type: "persona", url: "equipo.html", d: "Demo profile for the coordination team. Replace via the CMS." },
  { t: "Researchers at the Chair", type: "persona", url: "equipo.html#investigadores", d: "List of linked research profiles." }
];

/* Activities feed for the calendar and agenda (demo dates) */
window.CH_EVENTS = [
  { date: "2026-09-24", time: "17:00–19:00", title: "Ongoing seminar: Rethinking Hispanidad in the 21st Century", type: "Seminar", mode: "Hybrid", place: "University campus · Room to be confirmed", url: "actividad.html" },
  { date: "2026-10-08", time: "10:00–14:00", title: "Workshop: Archives, memory and shared heritage", type: "Workshop", mode: "In person", place: "Central library", url: "actividades.html" },
  { date: "2026-10-22", time: "18:00–19:30", title: "Public conversation: Language, identity and social change", type: "Conversation", mode: "In person", place: "Assembly hall", url: "actividades.html" },
  { date: "2026-11-12", time: "17:00–19:00", title: "Ongoing seminar · Session 2: Atlas and digital archives", type: "Seminar", mode: "Online", place: "Virtual classroom", url: "actividades.html" },
  { date: "2027-07-05", time: "09:30–14:00", title: "Summer course: History, culture and institutions of the Hispanic world", type: "Course", mode: "In person", place: "Summer courses venue", url: "actividades.html" }
];

/* Initial search suggestions */
window.CH_SUGGESTIONS = [
  { t: "Active projects", url: "proyectos.html?estado=activo", k: "Research" },
  { t: "Upcoming seminars", url: "actividades.html#proximas", k: "Activities" },
  { t: "Latest journal issue", url: "revista-numero-01.html", k: "Journal" },
  { t: "Leadership and team", url: "equipo.html", k: "People" },
  { t: "Open-access publications", url: "repositorio.html", k: "Library" }
];
