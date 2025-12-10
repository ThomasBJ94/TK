from typing import List, Tuple

from fastapi import FastAPI
from pydantic import BaseModel

# ---------- APP-OPSÆTNING ----------

app = FastAPI(
    title="Telika kephalaia Action",
    version="0.3.1",
    description=(
        "Topos-baseret inventio med FOR/IMOD ud fra: "
        "lovlighed, retfærdighed, nytte, nødvendighed, "
        "gennemførlighed, ære og konsekvenser."
    ),
)


# ---------- DATA-MODELLER ----------

class LolRequest(BaseModel):
    """Input til /lol-endpointet."""
    claim: str
    language: str = "da"
    max_topoi: int = 7  # hvor mange topoi der max skal med


class Argument(BaseModel):
    """Et enkelt argument under en given topos."""
    topos: str
    argument: str
    suggestions: List[str]


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


# ---------- LOGIK: GENERÉR ARGUMENTER FOR ÉN TOPOS ----------

def generate_arguments_for_topos(topos: str, claim: str) -> Tuple[Argument, Argument]:
    """
    Returnér (for-argument, imod-argument) for én topos.
    Teksterne er skabeloner, som du kan finpudse senere.
    """

    if topos == "Lovlighed":
        for_arg_text = (
            f"Ud fra lovlighedstopos kan man FOR påstanden '{claim}' hævde, "
            f"at den kan begrundes i gældende lovgivning eller i overordnede retsprincipper."
        )
        against_arg_text = (
            f"IMOD påstanden '{claim}' kan man ud fra lovlighedstopos hævde, "
            f"at den strider mod gældende regler, rettigheder eller retssikkerhed."
        )
        for_suggestions = [
            "Undersøg konkret lovgivning, paragraffer og praksis.",
            "Kobl til forfatningsmæssige eller menneskeretlige principper.",
            "Brug juridiske ekspertudtalelser.",
        ]
        against_suggestions = [
            "Peg på mulige lovbrud eller gråzoner.",
            "Fremhæv risici for retssikkerhed eller vilkårlighed.",
            "Sammenlign med tidligere domme eller afgørelser.",
        ]

    elif topos == "Retfærdighed":
        for_arg_text = (
            f"FOR påstanden '{claim}' kan man med retfærdighedstopos hævde, "
            f"at den bidrager til en mere rimelig og fair fordeling af byrder og goder."
        )
        against_arg_text = (
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

    elif topos == "Nytte":
        for_arg_text = (
            f"Ud fra nyttetopos kan man FOR påstanden '{claim}' hævde, "
            f"at den samlet set skaber størst mulig gavn for flest mulige."
        )
        against_arg_text = (
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

    elif topos == "Nødvendighed":
        for_arg_text = (
            f"FOR påstanden '{claim}' kan man fra nødvendighedstopos hævde, "
            f"at der ikke findes realistiske alternativer, hvis man vil undgå værre følger."
        )
        against_arg_text = (
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

    elif topos == "Gennemførlighed":
        for_arg_text = (
            f"Ud fra gennemførlighedstopos kan man FOR påstanden '{claim}' hævde, "
            f"at den er praktisk realistisk at implementere med de ressourcer, vi har."
        )
        against_arg_text = (
            f"IMOD påstanden '{claim}' kan man hævde, at den i praksis er vanskelig eller "
            f"uoverkommelig at gennemføre organisatorisk, politisk eller teknisk."
        )
        for_suggestions = [
            "Vis at de nødvendige ressourcer, kompetencer og strukturer er til stede.",
            "Peg på eksisterende pilotprojekter eller erfaringer.",
            "Lav en trinvis implementeringsplan.",
        ]
        against_suggestions = [
            "Peg på flaskehalse, modstand eller mangel på ressourcer.",
            "Brug erfaringer med tidligere fejlslagne implementeringer.",
            "Spørg hvem der konkret skal gøre hvad, hvornår og hvordan.",
        ]

    elif topos == "Ære":
        for_arg_text = (
            f"FOR påstanden '{claim}' kan man ud fra ærestopos hævde, "
            f"at den styrker vores omdømme, integritet eller moralske autoritet."
        )
        against_arg_text = (
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

    elif topos == "Konsekvenser":
        for_arg_text = (
            f"FOR påstanden '{claim}' kan man fra konsekvenstopos hævde, "
            f"at dens positive følgevirkninger (direkte og indirekte) vejer tungt."
        )
        against_arg_text = (
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

    else:
        # Fallback – burde ikke rammes, men er her for sikkerheds skyld
        for_arg_text = (
            f"FOR påstanden '{claim}' kan der ud fra '{topos}'-topos "
            f"formuleres generelle fordele."
        )
        against_arg_text = (
            f"IMOD påstanden '{claim}' kan der ud fra '{topos}'-topos "
            f"formuleres generelle ulemper."
        )
        for_suggestions = [
            "Uddyb topos nærmere.",
            "Brug konkrete eksempler.",
        ]
        against_suggestions = [
            "Uddyb topos nærmere.",
            "Brug konkrete eksempler.",
        ]

    for_arg = Argument(
        topos=topos,
        argument=for_arg_text,
        suggestions=for_suggestions,
    )
    against_arg = Argument(
        topos=topos,
        argument=against_arg_text,
        suggestions=against_suggestions,
    )

    return for_arg, against_arg


# ---------- ENDPOINT ----------

@app.post("/lol", response_model=LolResponse)
def lol_action(req: LolRequest) -> LolResponse:
    """
    /lol-endpointet:
    - tager imod en påstand
    - går systematisk topoi igennem
    - returnerer FOR/IMOD-argumenter per topos.
    """
    selected_topoi = TOPOI[: req.max_topoi]

    for_arguments: List[Argument] = []
    against_arguments: List[Argument] = []

    for t in selected_topoi:
        for_arg, against_arg = generate_arguments_for_topos(t, req.claim)
        for_arguments.append(for_arg)
        against_arguments.append(against_arg)

    return LolResponse(
        claim=req.claim,
        language=req.language,
        for_arguments=for_arguments,
        against=against_arguments,
    )

