from typing import List, Tuple, Optional, Literal, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

# ---------- APP-OPSÆTNING ----------

app = FastAPI(
    title="Telika kephalaia Action",
    version="0.3.3",
    description=(
        "Topos-baseret inventio med FOR/IMOD ud fra: "
        "lovlighed, retfærdighed, nytte, nødvendighed, "
        "gennemførlighed, ære og konsekvenser. "
        "Valgfrit: Burkeanske/pentadiske ratio-linser (ratio_mode)."
    ),
)


# ---------- PENTAD-RATIO BANK ----------

RatioMode = Literal["off", "light", "full"]

# Intern ratio_id -> menneskelig label + skabeloner
RATIO_BANK: Dict[str, Dict[str, str]] = {
    "scene_act": {
        "label": "Scene–Act (kontekst → handling)",
        "for": (
            "Givet scenen/konteksten ({scene_hint}), fremstår handlingen '{claim}' som "
            "en passende respons, fordi omstændighederne gør denne type tiltag forventeligt/tilpasset."
        ),
        "against": (
            "Netop fordi scenen/konteksten ({scene_hint}) ser ud som den gør, er handlingen '{claim}' "
            "misforholdt eller risikabel: konteksten peger på andre, mere proportionale skridt."
        ),
    },
    "act_scene": {
        "label": "Act–Scene (handling → ny kontekst)",
        "for": (
            "Hvis vi gennemfører '{claim}', skaber handlingen en ny scene/kontekst: "
            "incitamenter, normer eller rammer flyttes, så ønskede effekter bliver mere sandsynlige."
        ),
        "against": (
            "Hvis vi gennemfører '{claim}', skaber handlingen en scene/kontekst, hvor uønskede effekter "
            "bliver mere sandsynlige (fx omgåelse, skævvridning, mistillid eller systempres)."
        ),
    },
    "agent_act": {
        "label": "Agent–Act (aktør/ansvar → handling)",
        "for": (
            "Set som Agent–Act: Den/de relevante aktører bør handle i retning af '{claim}', "
            "fordi deres rolle, ansvar eller legitimitet netop forpligter dem til denne type handling."
        ),
        "against": (
            "Set som Agent–Act: Det er urimeligt at pålægge aktøren '{claim}', fordi handlingen ikke passer "
            "til aktørens mandat/rolle/ansvar – og ansvaret bør placeres andetsteds."
        ),
    },
    "act_agent": {
        "label": "Act–Agent (handling → karakter/legitimitet)",
        "for": (
            "Set som Act–Agent: At gennemføre '{claim}' signalerer ansvarlighed og integritet "
            "– og styrker aktørens legitimitet i den relevante offentlighed."
        ),
        "against": (
            "Set som Act–Agent: At gennemføre '{claim}' kan signalere hykleri, overgreb eller naivitet "
            "– og svækker dermed aktørens troværdighed/legitimitet."
        ),
    },
    "agency_act": {
        "label": "Agency–Act (midler → handlingens kvalitet)",
        "for": (
            "Set som Agency–Act: Med de rigtige midler/procedurer kan '{claim}' udføres præcist og proportionelt, "
            "så intentionen realiseres uden unødig skade."
        ),
        "against": (
            "Set som Agency–Act: Uden robuste midler/procedurer bliver '{claim}' enten symbolpolitik "
            "eller vilkårlig håndhævelse, hvilket undergraver både effekt og legitimitet."
        ),
    },
    "purpose_act": {
        "label": "Purpose–Act (mål → handling)",
        "for": (
            "Set som Purpose–Act: Hvis målet er ({purpose_hint}), følger '{claim}' som et konsistent skridt "
            "for at realisere dette telos."
        ),
        "against": (
            "Set som Purpose–Act: Hvis målet er ({purpose_hint}), er '{claim}' en omvej eller kontraproduktivt "
            "– andre handlinger realiserer målet mere sikkert/billigt/retfærdigt."
        ),
    },
    "act_purpose": {
        "label": "Act–Purpose (handling → afslører formål)",
        "for": (
            "Set som Act–Purpose: '{claim}' er ikke bare retorik; det er den type handling, der i praksis "
            "kan realisere et erklæret formål – og gør målet troværdigt."
        ),
        "against": (
            "Set som Act–Purpose: '{claim}' kan dække over et andet (u-udtalt) formål end det erklærede, "
            "fx kontrol/PR/omfordeling – hvilket bør problematiseres."
        ),
    },
}

# Hvilke ratioer passer typisk bedst til hvilke topoi (default-valg)
TOPOS_TO_DEFAULT_RATIOS: Dict[str, List[str]] = {
    "Lovlighed": ["agency_act", "act_purpose"],
    "Gennemførlighed": ["agency_act", "scene_act"],
    "Nytte": ["purpose_act", "act_scene"],
    "Konsekvenser": ["act_scene", "scene_act"],
    "Nødvendighed": ["scene_act", "purpose_act"],
    "Retfærdighed": ["agent_act", "act_agent"],
    "Ære": ["act_agent", "agent_act"],
}


# ---------- DATA-MODELLER ----------

class LolRequest(BaseModel):
    """Input til /lol-endpointet."""
    claim: str
    language: str = "da"

    max_topoi: int = Field(
        default=7,
        ge=1,
        le=7,
        description="Hvor mange topoi der max skal med (1-7).",
    )

    # Lovhenvisninger (Lovlighed + Gennemførlighed)
    legal_sources: Optional[List[str]] = Field(
        default=None,
        description=(
            "Liste over konkrete lovkilder/rammer, der er relevante for påstanden. "
            "Eksempler: 'Forvaltningsloven', 'Grundloven §73', 'EU GDPR (2016/679)', "
            "'OECD Pillar Two', 'Selskabsskatteloven §...'."
        ),
    )

    # NYT: Burke/pentad ratio-linse
    ratio_mode: RatioMode = Field(
        default="off",
        description=(
            "Pentadisk ratio-tilstand. "
            "'off' = ingen ratio, 'light' = 1 ratio pr. topos, 'full' = flere ratioer pr. topos."
        ),
    )

    ratios_per_topos: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Hvor mange ratioer pr. topos i ratio_mode='full' (1-4).",
    )

    ratios: Optional[List[str]] = Field(
        default=None,
        description=(
            "Valgfrit: styr hvilke ratioer der bruges (ratio_id). "
            "Mulige: " + ", ".join(sorted(RATIO_BANK.keys()))
        ),
    )


class Argument(BaseModel):
    """Et enkelt argument under en given topos (evt. med ratio-linse)."""
    topos: str
    argument: str
    suggestions: List[str]
    ratio_id: Optional[str] = None
    ratio: Optional[str] = None


class LolResponse(BaseModel):
    """Struktureret svar med argumenter for og imod."""
    claim: str
    language: str
    for_arguments: List[Argument]
    against: List[Argument]


# ---------- KONSTANT: DINE TOPOI ----------

TOPOI: List[str] = [
    "Lovlighed",
    "Retfærdighed",
    "Nytte",
    "Nødvendighed",
    "Gennemførlighed",
    "Ære",
    "Konsekvenser",
]


# ---------- HJÆLPERE ----------

def _format_legal_sources(legal_sources: Optional[List[str]], max_items: int = 3) -> str:
    """Formatér konkrete lovkilder til indlejring i argumenttekst."""
    if not legal_sources:
        return "— (Mangler konkret lovhenvisning: angiv relevante love/rammer i `legal_sources`.)"
    picked = [s.strip() for s in legal_sources if s and s.strip()][:max_items]
    if not picked:
        return "— (Mangler konkret lovhenvisning: angiv relevante love/rammer i `legal_sources`.)"
    return "; ".join(picked)


def _normalize_ratio_ids(requested: Optional[List[str]]) -> List[str]:
    """Filtrér/normalisér ratio_id'er til dem vi faktisk understøtter."""
    if not requested:
        return []
    out: List[str] = []
    for r in requested:
        rid = (r or "").strip()
        if rid in RATIO_BANK and rid not in out:
            out.append(rid)
    return out


def _pick_ratios_for_topos(
    topos: str,
    ratio_mode: RatioMode,
    ratios_per_topos: int,
    requested_ratio_ids: List[str],
) -> List[str]:
    """
    Vælg ratio_id'er for et givent topos.
    - off: []
    - light: 1 ratio (default pr. topos, eller første requested)
    - full: op til ratios_per_topos (prioritér requested, ellers defaults)
    """
    if ratio_mode == "off":
        return []

    defaults = TOPOS_TO_DEFAULT_RATIOS.get(topos, ["scene_act"])
    pool: List[str] = []

    # Requested ratioer får prioritet, men vi filtrerer til ratio-bank
    for rid in requested_ratio_ids:
        if rid in RATIO_BANK and rid not in pool:
            pool.append(rid)

    # Fyld op med defaults
    for rid in defaults:
        if rid in RATIO_BANK and rid not in pool:
            pool.append(rid)

    if ratio_mode == "light":
        return pool[:1]
    return pool[:ratios_per_topos]


def _ratio_text(
    ratio_id: str,
    side: Literal["for", "against"],
    claim: str,
    topos: str,
    legal_sources: Optional[List[str]],
) -> str:
    """
    Generér ratio-tekst (kort) til at bygge ind i argumentet.
    Vi bruger små 'hints' afhængigt af topos, så skabelonerne ikke bliver helt tomme.
    """
    sources_txt = _format_legal_sources(legal_sources)

    # Små hints, der giver ratioerne lidt “krog” uden at kræve ekstra inputfelter
    scene_hint = {
        "Lovlighed": f"retlige rammer og kompetencekrav ({sources_txt})",
        "Gennemførlighed": f"implementeringskrav, institutioner og ressourcer ({sources_txt})",
        "Nytte": "samfundsøkonomi, incitamenter og fordelingsvirkninger",
        "Konsekvenser": "risici, bivirkninger og second-order effects",
        "Nødvendighed": "tidspres, uomgængelige vilkår og handlingspres",
        "Retfærdighed": "byrdefordeling, ligheds- og rimelighedsnormer",
        "Ære": "troværdighed, identitet og normer i offentligheden",
    }.get(topos, "den relevante kontekst")

    purpose_hint = {
        "Nytte": "størst mulig gavn for flest mulige",
        "Konsekvenser": "minimering af skade og maksimering af positive følgevirkninger",
        "Nødvendighed": "at undgå værre følger under de givne vilkår",
        "Retfærdighed": "en mere rimelig fordeling af goder og byrder",
        "Ære": "at styrke integritet og moralsk autoritet",
        "Lovlighed": "at sikre legitim hjemmel og retsstatlighed",
        "Gennemførlighed": "at realisere intentionen i praksis",
    }.get(topos, "at realisere et legitimt mål")

    spec = RATIO_BANK[ratio_id]
    template = spec[side]
    return template.format(
        claim=claim,
        scene_hint=scene_hint,
        purpose_hint=purpose_hint,
        topos=topos,
        legal_sources=sources_txt,
    )


# ---------- LOGIK: GENERÉR ARGUMENTER FOR ÉN TOPOS ----------

def generate_arguments_for_topos(
    topos: str,
    claim: str,
    legal_sources: Optional[List[str]] = None,
    ratio_mode: RatioMode = "off",
    ratios_per_topos: int = 2,
    requested_ratio_ids: Optional[List[str]] = None,
) -> Tuple[List[Argument], List[Argument]]:
    """
    Returnér (liste af for-argumenter, liste af imod-argumenter) for én topos.
    - ratio_mode='off': 1+1 argument (som før)
    - ratio_mode='light': 1+1 argument med ratio-label + ratio-linse indbygget
    - ratio_mode='full': flere ratio-varianter pr. topos (op til ratios_per_topos)
    """
    requested_ratio_ids = requested_ratio_ids or []
    chosen_ratios = _pick_ratios_for_topos(
        topos=topos,
        ratio_mode=ratio_mode,
        ratios_per_topos=ratios_per_topos,
        requested_ratio_ids=requested_ratio_ids,
    )

    def _wrap(
        base_for_text: str,
        base_against_text: str,
        for_suggestions: List[str],
        against_suggestions: List[str],
    ) -> Tuple[List[Argument], List[Argument]]:
        # off: ingen ratio
        if ratio_mode == "off" or not chosen_ratios:
            return (
                [Argument(topos=topos, argument=base_for_text, suggestions=for_suggestions)],
                [Argument(topos=topos, argument=base_against_text, suggestions=against_suggestions)],
            )

        # light: 1 ratio (indbyg og label)
        if ratio_mode == "light":
            rid = chosen_ratios[0]
            rlabel = RATIO_BANK[rid]["label"]
            ratio_for = _ratio_text(rid, "for", claim, topos, legal_sources)
            ratio_against = _ratio_text(rid, "against", claim, topos, legal_sources)

            for_text = f"{base_for_text}\n\nRatio-linse: {rlabel}\n{ratio_for}"
            against_text = f"{base_against_text}\n\nRatio-linse: {rlabel}\n{ratio_against}"

            return (
                [Argument(topos=topos, argument=for_text, suggestions=for_suggestions, ratio_id=rid, ratio=rlabel)],
                [Argument(topos=topos, argument=against_text, suggestions=against_suggestions, ratio_id=rid, ratio=rlabel)],
            )

        # full: flere ratio-varianter pr. topos
        for_args: List[Argument] = []
        against_args: List[Argument] = []
        for rid in chosen_ratios:
            rlabel = RATIO_BANK[rid]["label"]
            ratio_for = _ratio_text(rid, "for", claim, topos, legal_sources)
            ratio_against = _ratio_text(rid, "against", claim, topos, legal_sources)

            for_text = f"{base_for_text}\n\nRatio-linse: {rlabel}\n{ratio_for}"
            against_text = f"{base_against_text}\n\nRatio-linse: {rlabel}\n{ratio_against}"

            for_args.append(Argument(topos=topos, argument=for_text, suggestions=for_suggestions, ratio_id=rid, ratio=rlabel))
            against_args.append(Argument(topos=topos, argument=against_text, suggestions=against_suggestions, ratio_id=rid, ratio=rlabel))

        return for_args, against_args

    # ----- Topos-specifik basisargumentation (som før) -----

    if topos == "Lovlighed":
        sources_txt = _format_legal_sources(legal_sources)

        base_for_text = (
            f"Ud fra lovlighedstopos kan man FOR påstanden '{claim}' hævde, at den kan hjemles "
            f"eller forankres i følgende konkrete lovkilder/rammer: {sources_txt}. "
            f"Argumentet styrkes ved at udpege præcis hjemmel (lov/§/artikel) og forklare, "
            f"hvordan den muliggør tiltaget."
        )
        base_against_text = (
            f"IMOD påstanden '{claim}' kan man ud fra lovlighedstopos hævde, at den kolliderer med "
            f"konkrete retsregler, rettigheder eller kompetenceregler, fx i: {sources_txt}. "
            f"Modargumentet styrkes ved at pege på den præcise regel (lov/§/artikel) og den "
            f"retlige konflikt (hjemmelsmangel, proportionalitet, lighedsgrundsætning, mv.)."
        )

        for_suggestions = [
            "Angiv *konkret hjemmel*: lov + paragraf / EU-forordning + artikel / bekendtgørelse + §.",
            "Angiv *kompetence*: hvilken myndighed har hjemlen, og via hvilken bestemmelse?",
            "Angiv *praksis*: relevante afgørelser/forarbejder/vejledninger (hvis kendt).",
        ]
        against_suggestions = [
            "Test for *hjemmelsmangel*: kræver tiltaget særskilt lovhjemmel?",
            "Peg på *rettighedskonflikt*: fx grundrettigheder, databeskyttelse, ligebehandling, mv.",
            "Peg på *procedureregler*: høring, proportionalitet, begrundelseskrav, klageadgang, mv.",
        ]
        return _wrap(base_for_text, base_against_text, for_suggestions, against_suggestions)

    if topos == "Gennemførlighed":
        sources_txt = _format_legal_sources(legal_sources)

        base_for_text = (
            f"Ud fra gennemførlighedstopos kan man FOR påstanden '{claim}' hævde, at den er "
            f"implementerbar gennem konkrete juridiske instrumenter og processer, fx via: {sources_txt}. "
            f"Argumentet styrkes ved at skitsere, *hvilken* lov-/regelændring eller *hvilken* "
            f"administrativ procedure der faktisk skal gennemføres (trinvis)."
        )
        base_against_text = (
            f"IMOD påstanden '{claim}' kan man hævde, at den i praksis er vanskelig at gennemføre, "
            f"fordi den kræver ændringer i konkret lovgivning, tværmyndighedskoordination eller "
            f"administrative procedurer, fx relateret til: {sources_txt}. "
            f"Modargumentet styrkes ved at pege på flaskehalse i lovproces/forvaltning/tilsyn/IT."
        )

        for_suggestions = [
            "Angiv *implementeringsvej*: lovforslag, bekendtgørelse, cirkulære, vejledning, kontrakt, mv.",
            "Angiv *myndighed + proces*: hvem udmønter, og hvilke formkrav gælder (høring, ikrafttræden, tilsyn)?",
            "Angiv *compliance*: hvordan håndhæves/reguleres det (tilsyn, sanktioner, rapportering)?",
        ]
        against_suggestions = [
            "Peg på *lovteknisk kompleksitet*: mange love, krydshenvisninger, EU-retlige bindinger, mv.",
            "Peg på *administrativ byrde*: data, kontrol, klagesager, ressourcebehov i myndigheder/aktører.",
            "Peg på *håndhævelse*: risiko for omgåelse, manglende sanktionsmuligheder, bevisproblemer, mv.",
        ]
        return _wrap(base_for_text, base_against_text, for_suggestions, against_suggestions)

    if topos == "Retfærdighed":
        base_for_text = (
            f"FOR påstanden '{claim}' kan man med retfærdighedstopos hævde, "
            f"at den bidrager til en mere rimelig og fair fordeling af byrder og goder."
        )
        base_against_text = (
            f"IMOD påstanden '{claim}' kan man hævde, at den skaber eller forværrer "
            f"uretfærdige forskelle mellem grupper eller individer."
        )
        for_suggestions = [
            "Vis hvem der vinder retfærdighed ved tiltaget.",
            "Brug fordelingsprincipper (lighed, behov, fortjeneste).",
            "Inddrag eksempler hvor lignende tiltag har virket retfærdigt.",
        ]
        against_suggestions = [
            "Peg på grupper, der stilles ringere uden god begrundelse.",
            "Sammenlign med idealer om lighed og ikke-diskrimination.",
            "Brug cases, hvor reformer opleves som uretfærdige.",
        ]
        return _wrap(base_for_text, base_against_text, for_suggestions, against_suggestions)

    if topos == "Nytte":
        base_for_text = (
            f"Ud fra nyttetopos kan man FOR påstanden '{claim}' hævde, "
            f"at den samlet set skaber størst mulig gavn for flest mulige."
        )
        base_against_text = (
            f"IMOD påstanden '{claim}' kan man med nyttetopos hævde, "
            f"at de samlede gevinster er begrænsede eller opvejes af betydelige omkostninger."
        )
        for_suggestions = [
            "Opgør gevinster i tal eller konkrete forbedringer.",
            "Kobl til samfundsøkonomi, trivsel eller effektivitet.",
            "Vis langsigtede nytteeffekter frem for kun kortsigtede.",
        ]
        against_suggestions = [
            "Fremhæv skjulte eller langsigtede omkostninger.",
            "Vis hvordan enkelte grupper betaler prisen for andres nytte.",
            "Sammenlign med alternative tiltag med større nytte.",
        ]
        return _wrap(base_for_text, base_against_text, for_suggestions, against_suggestions)

    if topos == "Nødvendighed":
        base_for_text = (
            f"FOR påstanden '{claim}' kan man fra nødvendighedstopos hævde, "
            f"at der ikke findes realistiske alternativer, hvis man vil undgå værre følger."
        )
        base_against_text = (
            f"IMOD påstanden '{claim}' kan man hævde, at nødvendighed påberåbes for hurtigt, "
            f"og at mulige alternativer eller mellemveje overses."
        )
        for_suggestions = [
            "Beskriv hvilke problemer der ellers vil opstå.",
            "Peg på tidspres, udefrakommende krav eller uomgængelige vilkår.",
            "Vis hvorfor alternativer realistisk set er lukkede.",
        ]
        against_suggestions = [
            "Identificér oversete alternativer eller kompromisser.",
            "Problematisér brugen af 'der er ikke noget valg'-retorik.",
            "Brug eksempler på, at lignende situationer er løst anderledes.",
        ]
        return _wrap(base_for_text, base_against_text, for_suggestions, against_suggestions)

    if topos == "Ære":
        base_for_text = (
            f"FOR påstanden '{claim}' kan man ud fra ærestopos hævde, "
            f"at den styrker vores omdømme, integritet eller moralske autoritet."
        )
        base_against_text = (
            f"IMOD påstanden '{claim}' kan man hævde, at den skader vores troværdighed, "
            f"værdighed eller selvforståelse som fællesskab."
        )
        for_suggestions = [
            "Kobl til identitet (nation, institution, profession).",
            "Vis hvordan tiltaget signalerer ansvarlighed eller mod.",
            "Brug eksempler på, at omdømme har haft konkret betydning.",
        ]
        against_suggestions = [
            "Peg på risiko for at fremstå hyklerisk eller utroværdig.",
            "Kobl til tidligere brud på idealer og løfter.",
            "Vis hvordan tiltaget strider mod udmeldte værdier.",
        ]
        return _wrap(base_for_text, base_against_text, for_suggestions, against_suggestions)

    if topos == "Konsekvenser":
        base_for_text = (
            f"FOR påstanden '{claim}' kan man fra konsekvenstopos hævde, "
            f"at dens positive følgevirkninger (direkte og indirekte) vejer tungt."
        )
        base_against_text = (
            f"IMOD påstanden '{claim}' kan man hævde, at dens negative følgevirkninger "
            f"(bivirkninger, utilsigtede effekter) er alvorlige."
        )
        for_suggestions = [
            "Skeln mellem kortsigtede og langsigtede konsekvenser.",
            "Brug scenarier eller fremskrivninger.",
            "Vis, hvem der vinder og taber på sigt.",
        ]
        against_suggestions = [
            "Fremhæv risici og usikkerhed.",
            "Beskriv worst case-scenarier uden at overdrive.",
            "Vis hvordan små ændringer kan give store negative effekter.",
        ]
        return _wrap(base_for_text, base_against_text, for_suggestions, against_suggestions)

    # fallback
    base_for_text = (
        f"FOR påstanden '{claim}' kan der ud fra '{topos}'-topos formuleres generelle fordele."
    )
    base_against_text = (
        f"IMOD påstanden '{claim}' kan der ud fra '{topos}'-topos formuleres generelle ulemper."
    )
    return _wrap(
        base_for_text,
        base_against_text,
        ["Uddyb topos nærmere.", "Brug konkrete eksempler."],
        ["Uddyb topos nærmere.", "Brug konkrete eksempler."],
    )


# ---------- ENDPOINT ----------

@app.post("/lol", response_model=LolResponse)
def lol_action(req: LolRequest) -> LolResponse:
    """
    /lol-endpointet:
    - tager imod en påstand
    - går systematisk topoi igennem
    - returnerer FOR/IMOD-argumenter per topos
    - valgfrit: ratio-linse pr. topos (ratio_mode)
    """
    selected_topoi = TOPOI[: req.max_topoi]
    requested_ratio_ids = _normalize_ratio_ids(req.ratios)

    for_arguments: List[Argument] = []
    against_arguments: List[Argument] = []

    for t in selected_topoi:
        for_list, against_list = generate_arguments_for_topos(
            topos=t,
            claim=req.claim,
            legal_sources=req.legal_sources,
            ratio_mode=req.ratio_mode,
            ratios_per_topos=req.ratios_per_topos,
            requested_ratio_ids=requested_ratio_ids,
        )
        for_arguments.extend(for_list)
        against_arguments.extend(against_list)

    return LolResponse(
        claim=req.claim,
        language=req.language,
        for_arguments=for_arguments,
        against=against_arguments,
    )

