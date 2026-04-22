#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create dialogues_TTM_Cheli_v2.txt — cheli-style improved translation of To The Moon
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# File reading helpers
# ─────────────────────────────────────────────────────────────────────────────

def read_utf16le(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] == b'\xff\xfe':
        raw = raw[2:]
    return raw.decode('utf-16-le').split('\r\n')


def write_utf16le(path, lines):
    text = '\r\n'.join(lines)
    data = b'\xff\xfe' + text.encode('utf-16-le')
    with open(path, 'wb') as f:
        f.write(data)


# ─────────────────────────────────────────────────────────────────────────────
# Structural line detection
# ─────────────────────────────────────────────────────────────────────────────

STRUCTURAL_KEYWORDS = ('MAP ', 'PAGE ', 'EVENT ', 'DMK ', 'MAP\t', 'PAGE\t')

# Regex to strip control codes so we can detect if dialogue text follows
_CTRL_RE = re.compile(r'\\[a-zA-Z.]+(\[[^\]]*\])?')


def is_structural(line):
    s = line.strip()
    if not s:
        return True
    # Separator lines
    if s.startswith('#') or s.startswith('/') or s.startswith('_'):
        return True
    if s.startswith('++++'):
        return True
    if s.startswith('-') and '[Map:' in s:
        return True
    for kw in STRUCTURAL_KEYWORDS:
        if s.startswith(kw):
            return True
    # Lines starting with backslash: structural only if no visible text follows
    # Remove all control codes; if nothing remains it's pure structural
    if s.startswith('\\'):
        remainder = _CTRL_RE.sub('', s).strip()
        return remainder == ''
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Cheli vocabulary — comprehensive replacement rules
# Each entry: (pattern, replacement, flags)
# Applied in order; patterns are regex.
# ─────────────────────────────────────────────────────────────────────────────

# Helper: build case-insensitive boundary replacements
def _r(pat, repl):
    return (re.compile(r'\b' + pat + r'\b', re.IGNORECASE), repl)


def _ri(pat, repl):
    """insensitive, no word boundary (for phrases with punctuation)"""
    return (re.compile(pat, re.IGNORECASE), repl)


# ── Vocabulary substitution table ────────────────────────────────────────────
# Ordered: most specific / longest first to avoid partial replacements
VOCAB_SUBS = [
    # === Money ===
    _r(r'el dinero',        'la pasta'),
    _r(r'el billete',       'la pasta'),
    _r(r'billetes',         'pasta'),
    _r(r'dinero',           'pasta'),

    # === People / Address ===
    _r(r'amigos',           'colegas'),
    _r(r'amigo',            'tío'),
    _r(r'amiga',            'tía'),
    _r(r'señor',            'tío'),
    _r(r'niños',            'chavales'),
    _r(r'niñas',            'chavales'),
    _r(r'niño',             'chaval'),
    _r(r'niña',             'chavala'),
    _r(r'chicos',           'chavales'),
    _r(r'chico',            'chaval'),
    _r(r'chica',            'chavala'),
    _r(r'gente',            'peña'),
    _r(r'personas',         'tíos'),
    _r(r'persona',          'tío'),
    _r(r'individuos',       'tíos'),
    _r(r'individuo',        'tío'),
    _r(r'tipos',            'tíos'),
    _r(r'muchacho',         'chaval'),
    _r(r'muchacha',         'chavala'),
    _r(r'adultos',          'mayores'),
    _r(r'adulto',           'mayor'),

    # === Death ===
    _ri(r'\bpalmar(la|la\b)',     r'palmar\1'),   # already cheli, keep
    _ri(r'\bmorir\b',            'palmar'),
    _ri(r'\bmuerto\b',           'palmado'),
    _ri(r'\bmuertos\b',          'palmados'),
    _ri(r'\bmuertes\b',          'palmaciones'),
    _ri(r'\bmuerte\b',           'muerte'),       # keep 'muerte' — too dramatic to replace
    _ri(r'\bfallecido\b',        'palmado'),
    _ri(r'\bfallecidos\b',       'palmados'),
    _ri(r'\bfallecer\b',         'palmarla'),
    _ri(r'\bfallece\b',          'palma'),

    # === Work ===
    _r(r'trabajando',       'currando'),
    _r(r'trabajo',          'curro'),
    _r(r'trabajar',         'currar'),
    _r(r'trabajas',         'curras'),
    _r(r'trabajamos',       'curramos'),
    _r(r'trabajan',         'curran'),
    _r(r'trabaja',          'curra'),
    _r(r'trabajé',          'curré'),

    # === Police ===
    _r(r'policías',         'maderos'),
    _r(r'policía',          'madero'),
    _r(r'agentes',          'maderos'),

    # === Alcohol / fun ===
    _r(r'cerveza',          'birra'),
    _r(r'cervezas',         'birras'),
    _r(r'alcohol',          'priva'),
    _r(r'beber',            'empinar el codo'),
    _r(r'bebida',           'priva'),

    # === Cool / bad / quality ===
    _ri(r'\bincreíble\b',        'flipante'),
    _ri(r'\bincreíbles\b',       'flipantes'),
    _ri(r'\bfantástico\b',       'de puta madre'),
    _ri(r'\bfantástica\b',       'de puta madre'),
    _ri(r'\bmaravilloso\b',      'guay'),
    _ri(r'\bmaravillosa\b',      'guay'),
    _ri(r'\bgenial\b',           'guay'),
    _ri(r'\bgeniales\b',         'guay del Paraguay'),
    _ri(r'\bexcelente\b',        'de primera'),
    _ri(r'\bexcelentes\b',       'de primera'),
    _ri(r'\bperfecto\b',         'perfecto'),     # keep
    _ri(r'\bperfecta\b',         'perfecta'),     # keep
    _ri(r'\bhorrible\b',         'chungo'),
    _ri(r'\bhorribles\b',        'chungos'),
    _ri(r'\bterrible\b',         'chungo'),
    _ri(r'\bterribles\b',        'chungos'),
    _ri(r'\bextraño\b',          'chungo'),
    _ri(r'\bextraña\b',          'chunga'),
    _ri(r'\bextraños\b',         'chungos'),
    _ri(r'\braro\b',             'chungo'),
    _ri(r'\brara\b',             'chunga'),

    # === Quantity ===
    _ri(r'\bmuchísimo\b',        'mogollón'),
    _ri(r'\bmuchísimos\b',       'mogollón de'),
    _ri(r'\bmuchísimas\b',       'mogollón de'),
    _ri(r'\bbastante\b',         'mazo'),
    _ri(r'\bbastantes\b',        'mazo'),
    _ri(r'\bmucho\b',            'mazo'),
    _ri(r'\bmucha\b',            'mazo'),
    _ri(r'\bmuchos\b',           'mogollón de'),
    _ri(r'\bmuchas\b',           'mogollón de'),

    # === Exclamations / fillers ===
    _ri(r'\bEn serio\b',         'En serio'),     # keep
    _ri(r'\bDe veras\b',         'En serio'),
    _ri(r'\bDe verdad\b',        'En serio'),
    _ri(r'\bRealmente\b',        'De verdad'),

    # === Mental state ===
    _ri(r'\bloco\b',             'pirado'),
    _ri(r'\bloca\b',             'pirada'),
    _ri(r'\blocos\b',            'pirados'),
    _ri(r'\blocas\b',            'piradas'),
    _ri(r'\bchiflado\b',         'pirado'),
    _ri(r'\bchiflada\b',         'pirada'),

    # === Situation / thing ===
    _ri(r'\bsituación\b',        'movida'),
    _ri(r'\bsituaciones\b',      'movidas'),
    _ri(r'\bproblema\b',         'rollo'),
    _ri(r'\bproblemas\b',        'rollos'),
    _ri(r'\bhistoria\b',         'rollo'),         # when informal
    _ri(r'\basunto\b',           'movida'),
    _ri(r'\bcosa\b',             'movida'),

    # === Affirmative / negative ===
    _ri(r'\bDesacuerdo\b',       'Ni de coña'),
    _ri(r'\bpara nada\b',        'ni de coña'),
    _ri(r'\bni hablar\b',        'ni de coña'),

    # === Informal registers ===
    _ri(r'\bguay\b',             'guay'),         # keep
    _ri(r'\bGracias\b',          'Gracias'),      # keep formal in most contexts
    _ri(r'\bpor supuesto\b',     'claro que sí'),
    _ri(r'\bdesde luego\b',      'claro'),
    _ri(r'\bpor favor\b',        'porfa'),
    _ri(r'\bde acuerdo\b',       'vale'),
    _ri(r'\bEn efecto\b',        'Exacto'),
    _ri(r'\bEfectivamente\b',    'Exacto'),
    _ri(r'\bBueno\b',            'Bueno'),        # keep
    _ri(r'\bEn realidad\b',      'A ver'),
    _ri(r'\bsin embargo\b',      'pero'),
    _ri(r'\bno obstante\b',      'pero'),
    _ri(r'\bademás\b',           'además'),       # keep
    _ri(r'\bde todas formas\b',  'de todas'),
    _ri(r'\bde todos modos\b',   'de todos modos'), # keep
    _ri(r'\bde hecho\b',         'a ver'),
    _ri(r'\bpr[aá]cticamente\b', 'casi'),

    # === Common phrase fixes (formal → informal) ===
    _ri(r'\bAvíseme\b',          'Avísanos'),
    _ri(r'\bustedes\b',          'vosotros'),
    _ri(r'\bUstedes\b',          'Vosotros'),

    # Specific dialogue improvements
    _ri(r'Tengo que ir a orinar',    'Tengo que mear'),
    _ri(r'tengo que ir a orinar',    'tengo que mear'),
    _ri(r'voy a orinar',             'voy a mear'),
    _ri(r'ir al baño',               'ir a mear'),
    _ri(r'al servicio',              'al baño'),
    _ri(r'necesito ir al baño',      'necesito mear'),
    _ri(r'reclamo del seguro',       'reclamación al seguro'),
    _ri(r'Será mejor que primero vayas a ver ese faro de afuera',
        'Mejor échale un ojo al faro ese de fuera primero'),
    _ri(r'Será mejor que les pregunte a esos niños primero',
        'Mejor preguntarle a esos chavales primero'),
    _ri(r'Debería preguntarles a esos niños primero',
        'Mejor pregunto a esos chavales'),
]


# ─────────────────────────────────────────────────────────────────────────────
# Character-specific voice rules
# These additional rules apply only when a specific speaker is active
# ─────────────────────────────────────────────────────────────────────────────

WATTS_SUBS = [
    # Dr. Watts: quick wit, irony, street-smart warmth
    _ri(r'\bEstá bien\b',     'Oye'),
    _ri(r'\bMuy bien\b',      'Guay'),
    _ri(r'\bVale, bien\b',    'Venga'),
    _ri(r'\bHola\b',          'Ey'),
    _ri(r'\bEy\b',            'Ey'),           # keep
    _ri(r'\bVamos\b',         'Venga va'),
    _ri(r'\bVenga\b',         'Venga'),        # keep
    _ri(r'\bEntiendo\b',      'Ya cacho'),
    _ri(r'\bEntendido\b',     'Pillado'),
    _ri(r'\bpor supuesto\b',  'claro que sí, tío'),
    _ri(r'\bSin duda\b',      'No hay tu tía'),
    _ri(r'\bSin problemas\b', 'Sin rollo'),
    _ri(r'\bEs complicado\b', 'Es un rollo'),
    _ri(r'\bEs extraño\b',    'Qué chungo'),
    _ri(r'\bqué raro\b',      'qué chungo'),
    _ri(r'\bEs bueno\b',      'Mola'),
    _ri(r'\bme gusta\b',      'mola'),
    _ri(r'\bMe gusta\b',      'Mola'),
    _ri(r'\bNo me gusta\b',   'No mola'),
]

ROSALENE_SUBS = [
    # Dr. Rosalene: cold precision, dry sarcasm, fewer words, more bite
    _ri(r'\bEstá bien\b',       'Bien'),
    _ri(r'\bMuy bien\b',        'Bien'),
    _ri(r'\bHola\b',            'Hola'),
    _ri(r'\bEntiendo\b',        'Entendido'),
    _ri(r'\bSin duda\b',        'Obviamente'),
    _ri(r'\bEs complicado\b',   'Complicado'),
    _ri(r'\bpor supuesto\b',    'por supuesto'),
    _ri(r'\bSin problemas\b',   'Sin problema'),
    _ri(r'\bpunks\b',           'punks'),       # keep as-is (it's in orig)
]

JOHNNY_SUBS = [
    # Johnny: simple emotional directness, vulnerable
    _ri(r'\bEstá bien\b',       'Vale'),
    _ri(r'\bSin duda\b',        'Claro'),
    _ri(r'\bEntiendo\b',        'Ya'),
    _ri(r'\bno lo sé\b',        'no sé'),
    _ri(r'\bNo lo sé\b',        'No sé'),
    _ri(r'\bde verdad\b',       'en serio'),
    _ri(r'\bDe verdad\b',       'En serio'),
]

RIVER_SUBS = [
    # River: fragile poetry, tender mystery
    _ri(r'\bEstá bien\b',       'Bien'),
    _ri(r'\bMovida\b',          'Cosa'),       # River speaks more pure/plain
    _ri(r'\bmovida\b',          'cosa'),
    _ri(r'\bRollo\b',           'Cosa'),
    _ri(r'\brollo\b',           'cosa'),
    _ri(r'\bPasta\b',           'Dinero'),     # River more formal
    _ri(r'\bpasta\b',           'dinero'),
    _ri(r'\bCurro\b',           'Trabajo'),
    _ri(r'\bcurro\b',           'trabajo'),
    _ri(r'\bChungo\b',          'Extraño'),
    _ri(r'\bchungo\b',          'extraño'),
]

LILY_SUBS = [
    # Lily: warm, everyday dignity
    _ri(r'\bEstá bien\b',       'Está bien'),
    _ri(r'\bMuy bien\b',        'Muy bien'),
    _ri(r'\bHola\b',            'Hola'),
]

SARAH_SUBS = [
    # Sarah: kid with attitude
    _ri(r'\bEstá bien\b',       'Vale'),
    _ri(r'\bMuy bien\b',        'Guay'),
    _ri(r'\bBueno\b',           'Bueno'),
]

TOMMY_SUBS = [
    # Tommy: simple kid
    _ri(r'\bEstá bien\b',       'Sí'),
    _ri(r'\bMuy bien\b',        'Bien'),
]

CHARACTER_SUBS = {
    'Dr. Watts':    WATTS_SUBS,
    'Dr. Rosalene': ROSALENE_SUBS,
    'Johnny':       JOHNNY_SUBS,
    'River':        RIVER_SUBS,
    'Lily':         LILY_SUBS,
    'Sarah':        SARAH_SUBS,
    'Tommy':        TOMMY_SUBS,
}


# ─────────────────────────────────────────────────────────────────────────────
# Specific line-level manual overrides
# Key = exact original English line (stripped), Value = cheli translation
# These override any automatic translation for key dramatic/important lines
# ─────────────────────────────────────────────────────────────────────────────

MANUAL_OVERRIDES = {
    # Opening scene
    '"Thanks for coming on such a short notice." ':
        '"Gracias por venir tan rápido." ',
    '"That\'s okay, \\.I tend to be bad at':
        '"Tranquila, \\. yo también soy un desastre para',
    'predicting deaths as well."':
        'calcular cuándo palma la gente."',
    '"Are you the patient\'s daughter?"':
        '"¿Es usted la hija del paciente?"',
    '"Oh no, \\.I am just his caretaker."  ':
        '"Oh no, \\.Solo soy su cuidadora."  ',
    '". . . And these are my children, \\.Sarah and Tommy." ':
        '". . . Y estos son mis hijos, \\.Sarah y Tommy." ',
    '"It\'s not exactly a nine-to-five job, \\.':
        '"No es exactamente un curro de nueve a cinco, \\.',
    'so Johnny lets us live here."':
        'así que Johnny nos deja vivir aquí."',
    '"I suppose this \'Johnny\' is our man?" ':
        '"Supongo que este \'Johnny\' es nuestro hombre." ',
    '" . . . \'Johnny\'?" ':
        '" . . . ¿\'Johnny\'?" ',
    '"Listen, \\.\\.if it\'s a kid we\'re dealing with,\\.':
        '"Oye, \\.\\.si es un chaval con quien estamos tratando,\\.',
    'I don\'t think we\'re the ones you want." ':
        'creo que no somos los que quieres." ',
    '"No,\\. no. \\.\\.He just prefers to be called that." ':
        '"No, \\. no. \\.\\. Es que prefiere que lo llamen así." ',
    '"He\'s upstairs right now with his medical doctor." ':
        '"Está arriba ahora mismo con su médico." ',
    '"Come with me." ':
        '"Venid conmigo." ',
    '"C\'mon, \\.grab that case and let\'s go." ':
        '"Venga, \\. coge ese maletín y vámonos." ',
    '". . . When my back breaks one day,\\.':
        '". . . Cuando un día me revienten la espalda,\\.',
    ' I\'ll sue you with the insurance claim."':
        ' te pongo una denuncia y te arruino."',
    '"Where are you going?"':
        '"¿Adónde vas?"',
    '". . . I gotta go take a leak."':
        '". . . Tengo que ir a mear."',
    '"Ok, \\.they\'re gone!" ':
        '"Guay, \\. ¡se han pirado!" ',
    '"Whoever gets there first gets to play the melody!!"':
        '"¡¡Quien llegue primero toca la melodía!!"',
    '"No fair! \\.You pushed me." ':
        '"¡No hay derecho! \\.Me empujaste." ',
    '"What do you punks want?" ':
        '"¿Y vosotros qué queréis, gamberros?" ',
    '"We want. . .\\.\\. one \\itrillion\\i dollars!"':
        '"Queremos... .\\.\\. ¡un \\ibillón\\i de pesetas!"',
    '"Or the candycane mom hides from us."':
        '"O el bastón de caramelo que mamá nos esconde."',
    '"Yah, \\.\\.or that!" ':
        '"¡Sí, \\.\\.o eso!" ',
    '". . . Alright, \\.\\.let\'s talk."':
        '". . . Muy bien, \\.\\. a ver qué queréis."',
    '"Er, \\.what?" ':
        '"Eeh, \\.¿cómo?" ',

    # Chapter 1 / medical staff
    '"He is unresponsive at this point, but by the looks of ':
        '"No responde en este momento, pero por cómo pinta ',
    'things, \\.he\'s still consciously hanging on." ':
        'la cosa, \\. todavía aguanta consciente." ',
    '"It\'s hard to say how long you\'ll have, \\.':
        '"Es difícil decir cuánto tiempo os queda, \\.',
    'but I would hurry." ':
        'pero yo me daría prisa." ',
    '"Here, \\.\\.take this."':
        '"Toma, \\.\\. quédate con esto."',
    '"That\'ll keep you updated on Johnny\'s status."':
        '"Así estaréis al tanto del estado de Johnny."',
    '"I hope there\'s no self-destruct button. . .':
        '"Espero que no tenga botón de autodestrucción...',
    '\\.I seem to have a knack for those."':
        '\\.Tengo un talento especial para esas movidas."',
    '"Thanks, \\.I was just going to ask for it."':
        '"Gracias, \\. justo iba a pedirlo."',

    # Kids dialogue improvements
    '"If grown-ups get to drink coffee, \\.does that mean ':
        '"Si los mayores pueden tomar café, \\.¿eso significa ',
    'grown-ups don\'t really have to sleep??" ':
        'que los mayores no tienen que dormir??" ',
    '"Ma says not to go in that room today." ':
        '"Mamá dice que hoy no entremos en esa habitación." ',
    '"Which is awesome, \\.because we can stay up late!" ':
        '"¡Qué guay, \\. porque podemos quedarnos despiertos hasta tarde!" ',
    '"I\'m tired . . . it\'s like seven billion o\'clock already!!" ':
        '"Estoy muerto... ¡¡ya son como las siete mil millones en punto!!" ',
    '"Ma says not to go in that room."  ':
        '"Mamá dice que no entremos en esa habitación."  ',
    '"But our bunk\'s in there, \\.and now we can\'t sleep!" ':
        '"¡Pero nuestra litera está ahí, \\. y ahora no podemos dormir!" ',

    # Choice lines
    '( Better go check out that lighthouse outside first. )':
        '( Mejor echarle un ojo al faro ese de fuera primero. )',
    '( I should ask those kids first. )':
        '( Mejor pregunto a esos chavales primero. )',
    "( I'd better ask those kids first. )":
        '( Mejor les pregunto a esos chavales primero. )',
    "( This isn't the kitchen. )":
        '( Esta no es la cocina. )',
    "( The kitchen's at the other door. )":
        '( La cocina está en la otra puerta. )',
    'Go upstairs?':
        '¿Subir arriba?',
    'Go inside anyways?':
        '¿Entrar de todas formas?',
    'Show around the house.':
        'Enseñar la casa.',
    'Keep playing.':
        'Seguir jugando.',
    'Yes':     'Sí',
    'No':      'No',

    # General guide hints
    '[ . . . The patient is waiting upstairs, \\.':
        '[ . . . El paciente está esperando arriba, \\.',
    'better not waste time. ]':
        'mejor no perder el tiempo. ]',

    # Medical monitoring
    "Johnny's heart monitor is now activated in menu.":
        'El monitor cardíaco de Johnny ya está activado en el menú.',

    # Tour of house
    '"Hey, \\.your ma told you to show me ':
        '"Oye, \\. tu madre te ha dicho que me enseñes ',
    'around the house." ':
        'la casa." ',
    '"Sarah and Tommy, \\.right?"':
        '"Sarah y Tommy, \\.¿verdad?"',
    '"Your mother said to ask you two to ':
        '"Vuestra madre ha dicho que os pidamos ',
    'show me around the house."':
        'que nos enseñéis la casa."',
    '"Okay, \\.maybe we will."':
        '"Bueno, \\.a lo mejor sí."',
    '"Maybe. . . ?" ':
        '"¿A lo mejor...?" ',
    '". . . I think we just need a little ':
        '". . . Creo que solo nos hace falta un poco de ',
    'convincing, \\.that\'s all!"':
        'convencimiento, \\.¡eso es todo!"',
    '"Wut do ya think,\\.\\. Tommy?"':
        '"¿Tú qué dices, \\.\\. Tommy?"',
    '"Yah!" ':
        '"¡Sí!" ',
    '"Wha\'cha want?"  ':
        '"¿Qué quieres?"  ',
    '"Let me know if I can be of any assistance."  ':
        '"Avisad si puedo ayudar en algo."  ',
    '"Go on.\\.\\. I\'ll watch over his physical':
        '"Continuad.\\.\\. Yo vigilaré su estado físico',
    'conditions through the procedure."':
        'durante el procedimiento."',

    '"It\'s probably a decade old and tastes like rubber, ':
        '"Probablemente tiene diez años y sabe a goma, ',
    '\\.but you can use it like a walking-stick."':
        '\\.pero te sirve de bastón."',
    '"Okay, \\.I got what you wanted.':
        '"Vale, \\. aquí tienes lo que querías.',
    '\\.\\.. . . Good ol\' \\oi[34]."':
        '\\.\\... . El viejo \\oi[34]."',
    '"If you come and give me a tour at ':
        '"Si vienes a hacerme un recorrido ahora ',
    'this instant, \\.\\.I won\'t sneeze on it."':
        'mismo, \\.\\. no estornudo encima."',
    '"The kitchen door is right beside':
        '"La puerta de la cocina está justo al lado',
    'the stairs! \\.\\.Go fetch it!!" ':
        'de las escaleras! \\.\\.¡Ve a buscarlo!!" ',
    '". . . Ever asked your mom for a dog?"':
        '"... ¿Alguna vez le has pedido un perro a tu madre?"',
    '". . . You\'re more bossy than my real boss."':
        '"... Eres más mandona que mi jefe de verdad."',

    # Alright patterns (Watts voice)
    '"Alright kiddos, \\.\\.I was against a lot of':
        '"Muy bien chavales, \\.\\.tuve que pelear contra mogollón de',
    'odds back there, \\.but I got the \\oi[34]."':
        'cosas, \\.pero me hice con el \\oi[34]."',

    # Neil / others
    '( Better go see if Neil has any ideas. )':
        '( Mejor ver si Neil tiene alguna idea. )',
    '( . . . Ugh, \\.\\.you can smell that squirrel Neil ':
        '( . . . Uf, \\.\\.ya se huele esa ardilla que atropelló Neil ',
    'ran over all the way from here now. . . )':
        'desde aquí. . . )',

    # Young Johnny dialogue
    '"What the heck\'s a platypus?':
        '"¿Qué narices es un ornitorrinco?',
    '\\.Quit making words up." ':
        '\\.Deja de inventar palabras." ',
    '"Anyway, \\.she\'s just so . . . \\ioff\\i, y\'know?"':
        '"A ver, \\. ella es tan... . . . \\ioff\\i, ¿me entiendes?"',
    '"I know! \\.\\.Isn\'t that cool?" ':
        '"¡Ya! \\.\\. ¿No mola cantidad?" ',
    '"Being strange isn\'t always a good ':
        '"Ser chungo no siempre es bueno ',
    '"She\'s not just shy, \\.\\.Nick." ':
        '"No es solo tímida, \\.\\.Nick." ',
    '"There\'s something strange about her."':
        '"Hay algo chungo en ella."',
    '"Well,\\.\\. for one, \\.I don\'t wanna ruin my hair."':
        '"Bueno, \\.\\. para empezar, \\.no quiero estropearme el pelo."',
    '"I just . . . \\.\\.I just don\'t wanna be another ':
        '"Es que... . . . \\.\\.es que no quiero ser otro ',
    'typical kid in a sea of typical people."':
        'chaval de manual en un mar de peña de manual."',
    '"I mean, \\.\\.you\'d just be some guy who ':
        '"O sea, \\.\\.serías simplemente un tío que ',
    'hangs out with a shy girl." ':
        'sale con una tía tímida." ',
    '"But really, \\.\\.if you wanna be weird, \\.\\.why don\'t ':
        '"Pero en serio, \\.\\.si quieres ser el raro, \\.\\.¿por qué no te',
    'you just go hang with the emos and goths?"':
        'juntas con los emos y los góticos?"',
    '"The fact that we got a name for them says a lot too."':
        '"El hecho de que ya les hayamos puesto nombre dice mogollón."',
    '"She just sits there by herself all day, \\.with that ':
        '"Está todo el día sola ahí sentada, \\.con ese ',
    'creepy deformed duck toy." ':
        'juguete chungo de pato deforme." ',
    '"That\'s not a deformed duck. \\.That\'s a platypus."':
        '"No es un pato deforme. \\.Eso es un ornitorrinco."',
    '"It\'s like she\'s from a totally different ':
        '"Es que parece de un mundo totalmente diferente. ',
    'planet or something." ':
        'o algo así." ',
    '"But how the heck would being with her':
        '"Pero ¿cómo narices va a cambiar estar con ella',
    'change your own identity?!"':
        'tu propia identidad?!"',
    '"Look, \\.\\.Nick, \\."':
        '"Mira, \\.\\.Nick, \\."',
    '"I mean, \\.\\.just look at her!" ':
        '"A ver, \\.\\.¡solo mírala!" ',
}



# ─────────────────────────────────────────────────────────────────────────────
# Detect current character from \nm tag
# ─────────────────────────────────────────────────────────────────────────────

NM_RE = re.compile(r'\\nm\[\s*([^\]]+?)\s*\]')


def get_character(line):
    m = NM_RE.search(line)
    if m:
        name = m.group(1).strip()
        # Normalize
        for key in CHARACTER_SUBS:
            if key.lower() in name.lower():
                return key
        return name
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Apply cheli transformations to a dialogue line
# ─────────────────────────────────────────────────────────────────────────────

def apply_subs(text, subs):
    for pat, repl in subs:
        text = pat.sub(repl, text)
    return text


# Pre-build stripped-key lookup for faster / correct override matching
_OVERRIDES_STRIPPED = {k.rstrip(): v for k, v in MANUAL_OVERRIDES.items()}


def translate_dialogue(orig_line, cheli_line, character):
    """Improve a dialogue line from enriched cheli base."""

    # 1. Check manual override (keyed on original English, trailing-space-insensitive)
    stripped_orig = orig_line.rstrip()
    if stripped_orig in _OVERRIDES_STRIPPED:
        override = _OVERRIDES_STRIPPED[stripped_orig]
        trail_len = len(cheli_line.rstrip())
        trail = len(cheli_line) - trail_len
        if trail > 0:
            return override.rstrip() + cheli_line[trail_len:]
        return override

    # 2. Start from the enriched Spanish line as base
    result = cheli_line

    # 3. Apply global cheli vocabulary substitutions
    result = apply_subs(result, VOCAB_SUBS)

    # 4. Apply character-specific subs
    if character and character in CHARACTER_SUBS:
        result = apply_subs(result, CHARACTER_SUBS[character])

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Main processing
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("Reading files...")
    lines_orig  = read_utf16le('dialogues_TTM_orig.txt')
    lines_cheli = read_utf16le('dialogues_TTM_Cheli(enriched).txt')

    print(f"Original lines: {len(lines_orig)}")
    print(f"Cheli lines:    {len(lines_cheli)}")

    assert len(lines_orig) == len(lines_cheli), \
        f"Line count mismatch: {len(lines_orig)} vs {len(lines_cheli)}"

    output = []
    current_char = None
    prev_was_structural = True

    for i, (orig, cheli) in enumerate(zip(lines_orig, lines_cheli)):

        # Track current character
        c = get_character(orig)
        if c:
            current_char = c

        if is_structural(orig):
            # Always copy structural lines exactly from original
            output.append(orig)
            prev_was_structural = True
        else:
            # Dialogue line — apply cheli improvements
            improved = translate_dialogue(orig, cheli, current_char)
            output.append(improved)
            prev_was_structural = False

    print(f"Output lines: {len(output)}")

    output_path = 'dialogues_TTM_Cheli_v2.txt'
    write_utf16le(output_path, output)
    print(f"Written: {output_path}")

    # Verification
    verify = read_utf16le(output_path)
    print(f"Verification line count: {len(verify)}")
    assert len(verify) == len(lines_orig), \
        f"Output line count mismatch: {len(verify)} vs {len(lines_orig)}"
    print("✓ Line count correct!")

    # Show sample of changes
    print("\n=== Sample of improvements (first 20 changed lines) ===")
    changes = 0
    for i, (orig, cheli, out) in enumerate(zip(lines_orig, lines_cheli, output)):
        if not is_structural(orig) and out != cheli:
            print(f"L{i:5d}  ORIG:  {repr(orig[:75])}")
            print(f"       CHELI: {repr(cheli[:75])}")
            print(f"       NEW:   {repr(out[:75])}")
            print()
            changes += 1
            if changes >= 20:
                break
    changed_count = sum(
        1 for o, c, out in zip(lines_orig, lines_cheli, output)
        if not is_structural(o) and out != c
    )
    print(f"Total lines changed: {changed_count}")


if __name__ == '__main__':
    main()
