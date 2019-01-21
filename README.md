# Berlin

Berlin is a library that can be used for referencing international geographic locations. UN/LOCODE (United nations Code for Trade & Transport Locations) is used to return location information based on matches generated from the place name input. See below for examples.

## License

AGPLv3 in LICENSE file.

## Notes

Subdivisions in LOCODE list seem to be ISO3166-2:1998, not current ISO3166-2.

## Setup
<ul>
<li>git clone git@github.com:flaxandteal/berlin</li>
<br>
<li>install python3</li>
<br>
<li>install pipenv </li>
<br>
<li>run pipenv shell</li>
<br>
<li>pip install -r requirements.txt</li>
<br>
<li>sudo apt install libspatialindex-c4v5 (**linux command**)</li> 
<br>
<li>sudo apt install python3-Levenshtein && pip install python-Levenshtein (**linux command**)</li>
<br>
<li>git submodule update --init</li>

<hr>

# Use

## Find a geographical location

Input: 
<pre><code> Q Belfast </code></pre>
Returns: 
<pre><code>{'name': 'Belfast'}
MATCH(GB:BEL:2.250):
NAME MATCH:2.0:Belfast
FUNCTION COEFFICIENT:0.25:2.5
    GB:BEL
    [DEhgisawdxxaszs] <LOCODE [GB:BEL] for Belfast, Belfast, United Kingdom of Great Britain and Northern Ireland F2.5>
    [DF] Belfast, Belfast, United Kingdom of Great Britain and Northern Ireland
<br>    
    NAME: Belfast
    SUPERCODE: GB
    SUBCODE: BEL
    SUBDIVISION_NAME: Belfast
    SUBDIVISION_CODE: BFS
    FUNCTION_CODE: 1--4-6--
    IATA_OVERRIDE: BFS
    ALTERNATIVE NAMES: [Belfast]
    <br>  
    [Subdivision]
    <br>  
    GB:BFS
        [DE] <SubDivision [GB:BFS] for Belfast>
        [DF] Belfast, United Kingdom of Great Britain and Northern Ireland
        <br>  
        NAME: Belfast
        SUPERCODE: GB
        SUBCODE: BFS
        LEVEL: district council area
        ALTERNATIVE NAMES: [Belfast]
        <br>  
        [State]
            GB
            [DE] <State [GB] for United Kingdom of Great Britain and Northern Ireland>
            [DF] United Kingdom of Great Britain and Northern Ireland, GB-GBR
            <br>  
            NAME: United Kingdom of Great Britain and Northern Ireland
            SHORT: UK
            ALPHA2: GB
            ALPHA3: GBR
            OFFICIAL_EN: United Kingdom of Great Britain and Northern Ireland
            OFFICIAL_FR: Royaume-Uni de Grande-Bretagne et d'Irlande du Nord
            CONTINENT: EU
            ALTERNATIVE NAMES: [United Kingdom of Great Britain and Northern Ireland]
    <br>  
    [Functions]
    Port, as defined in Rec 16
    Airport
    Multimodal Functions (ICDs, etc.)
    </code></pre>
  
## Find based on closest match
  
### Returns the 3 closest results
  
Input: <pre><code> Q 3 bulfest</code></pre>

Returns: <pre><code>{'name': 'bulfest'}
MATCH(FR:BES:1.606):
NAME MATCH:1.206:bulfest
FUNCTION COEFFICIENT:0.4:4
    FR:BES
    [DE] <LOCODE [FR:BES] for Brest, Finistère, France F4.0>
    [DF] Brest, Finistère, France
    <br>  
    NAME: Brest
    SUPERCODE: FR
    SUBCODE: BES
    SUBDIVISION_NAME: Finistère
    SUBDIVISION_CODE: 29
    FUNCTION_CODE: 1234----
    CITY: Brest/Guipavas
    ALTERNATIVE NAMES: [Brest]
    <br>  
    [Subdivision]
        FR:29
        [DE] <SubDivision [FR:29] for Finistère>
        [DF] Finistère, France
        <br>  
        NAME: Finistère
        SUPERCODE: FR
        SUBCODE: 29
        LEVEL: metropolitan department
        ALTERNATIVE NAMES: [Finistère]
        <br>  
        [State]
            FR
            [DE] <State [FR] for France>
            [DF] France, FR-FRA
            <br>  
            NAME: France
            SHORT: France
            ALPHA2: FR
            ALPHA3: FRA
            OFFICIAL_EN: France
            OFFICIAL_FR: France
            CONTINENT: EU
            ALTERNATIVE NAMES: [France]
    <br>  
    [Functions]
    Port, as defined in Rec 16
    Rail Terminal
    Road Terminal
    Airport
    <br>  
    [IATA]
        BES
        [DE] <IATA [BES] for Brest Bretagne Airport>
        [DF] Brest Bretagne Airport, BES
        <br>  
        NAME: Brest Bretagne Airport
        TYPE: medium_airport
        CITY: Brest/Guipavas
        COUNTRY: FR
        REGION: FR-E
        IATA: BES
        Y: -4.418540000915527
        X: 48.447898864746094
        ELEVATION: 325
        ALTERNATIVE NAMES: [Brest Bretagne Airport]
MATCH(GB:BEL:1.528):
NAME MATCH:1.2779999999999998:bulfest
FUNCTION COEFFICIENT:0.25:2.5
    GB:BEL
    [DE] <LOCODE [GB:BEL] for Belfast, Belfast, United Kingdom of Great Britain and Northern Ireland F2.5>
    [DF] Belfast, Belfast, United Kingdom of Great Britain and Northern Ireland
    <br>  
    NAME: Belfast
    SUPERCODE: GB
    SUBCODE: BEL
    SUBDIVISION_NAME: Belfast
    SUBDIVISION_CODE: BFS
    FUNCTION_CODE: 1--4-6--
    IATA_OVERRIDE: BFS
    ALTERNATIVE NAMES: [Belfast]
    <br>  
    [Subdivision]
        GB:BFS
        [DE] <SubDivision [GB:BFS] for Belfast>
        [DF] Belfast, United Kingdom of Great Britain and Northern Ireland
        <br>  
        NAME: Belfast
        SUPERCODE: GB
        SUBCODE: BFS
        LEVEL: district council area
        ALTERNATIVE NAMES: [Belfast]
        <br>  
        [State]
            GB
            [DE] <State [GB] for United Kingdom of Great Britain and Northern Ireland>
            [DF] United Kingdom of Great Britain and Northern Ireland, GB-GBR
            <br>  
            NAME: United Kingdom of Great Britain and Northern Ireland
            SHORT: UK
            ALPHA2: GB
            ALPHA3: GBR
            OFFICIAL_EN: United Kingdom of Great Britain and Northern Ireland
            OFFICIAL_FR: Royaume-Uni de Grande-Bretagne et d'Irlande du Nord
            CONTINENT: EU
           <br>  
 ALTERNATIVE NAMES: [United Kingdom of Great Britain and Northern Ireland]
    <br>  
    [Functions]
    Port, as defined in Rec 16
    Airport
    Multimodal Functions (ICDs, etc.)
MATCH(BE:BRU:1.516):
NAME MATCH:1.1159999999999999:bulfest
FUNCTION COEFFICIENT:0.4:4
    BE:BRU
    [DE] <LOCODE [BE:BRU] for Bruxelles, Bruxelles-Capitale, Région de, Belgium F4.0>
    [DF] Bruxelles, Bruxelles-Capitale, Région de, Belgium
    <br>  
    NAME: Bruxelles
    SUPERCODE: BE
    SUBCODE: BRU
    SUBDIVISION_NAME: Bruxelles-Capitale, Région de
    SUBDIVISION_CODE: BRU
    FUNCTION_CODE: 1234----
    CITY: Brussels
    ALTERNATIVE NAMES: [Bruxelles]
    <br>  
    [Subdivision]
        BE:BRU
        [DE] <SubDivision [BE:BRU] for Bruxelles-Capitale, Région de>
        [DF] Bruxelles-Capitale, Région de, Belgium
        <br>  
        NAME: Bruxelles-Capitale, Région de
        SUPERCODE: BE
        SUBCODE: BRU
        LEVEL: province
        ALTERNATIVE NAMES: [Bruxelles-Capitale, Région de]
        <br>  
        [State]
            BE
            [DE] <State [BE] for Belgium>
            [DF] Belgium, BE-BEL
            <br>  
            NAME: Belgium
            SHORT: Belgium
            ALPHA2: BE
            ALPHA3: BEL
            OFFICIAL_EN: Belgium
            OFFICIAL_FR: Belgique
            CONTINENT: EU
            ALTERNATIVE NAMES: [Belgium]
    <br>  
    [Functions]
    Port, as defined in Rec 16
    Rail Terminal
    Road Terminal
    Airport
    <br>  
    [IATA]
        BRU
        [DE] <IATA [BRU] for Brussels Airport>
        [DF] Brussels Airport, BRU
        <br>  
        NAME: Brussels Airport
        TYPE: large_airport
        CITY: Brussels
        COUNTRY: BE
        REGION: BE-BRU
        IATA: BRU
        Y: 4.48443984985
        X: 50.901401519800004
        ELEVATION: 184
        ALTERNATIVE NAMES: [Brussels Airport]</code></pre>
<br>  

## Find based on state
Returns the results in the state specified ('GB' = Great Britain)
Input: 
<pre><code>QS GB bulfest</code></pre>
<br>  
Returns: <pre><code>{'name': 'bulfest'}
MATCH(GB:BEL:1.528):
NAME MATCH:1.2779999999999998:bulfest
FUNCTION COEFFICIENT:0.25:2.5
    GB:BEL
    [DE] <LOCODE [GB:BEL] for Belfast, Belfast, United Kingdom of Great Britain and Northern Ireland F2.5>
    [DF] Belfast, Belfast, United Kingdom of Great Britain and Northern Ireland
    <br>  
    NAME: Belfast
    SUPERCODE: GB
    SUBCODE: BEL
    SUBDIVISION_NAME: Belfast
    SUBDIVISION_CODE: BFS
    FUNCTION_CODE: 1--4-6--
    IATA_OVERRIDE: BFS
    ALTERNATIVE NAMES: [Belfast]
    <br>  
    [Subdivision]
        GB:BFS
        [DE] <SubDivision [GB:BFS] for Belfast>
        [DF] Belfast, United Kingdom of Great Britain and Northern Ireland
        <br>  
        NAME: Belfast
        SUPERCODE: GB
        SUBCODE: BFS
        LEVEL: district council area
        ALTERNATIVE NAMES: [Belfast]
        <br>  
        [State]
            GB
            [DE] <State [GB] for United Kingdom of Great Britain and Northern Ireland>
            [DF] United Kingdom of Great Britain and Northern Ireland, GB-GBR
            <br>  
            NAME: United Kingdom of Great Britain and Northern Ireland
            SHORT: UK
            ALPHA2: GB
            ALPHA3: GBR
            OFFICIAL_EN: United Kingdom of Great Britain and Northern Ireland
            OFFICIAL_FR: Royaume-Uni de Grande-Bretagne et d'Irlande du Nord
            CONTINENT: EU
            ALTERNATIVE NAMES: [United Kingdom of Great Britain and Northern Ireland]
    <br>  
    [Functions]
    Port, as defined in Rec 16
    Airport
    Multimodal Functions (ICDs, etc.)
</code></pre>
<br>  


