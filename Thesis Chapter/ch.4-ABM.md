# Chapter 4: Agent-Based Model of Iron Age IIA Settlement

## 4.1 Model Conceptualization and Rationale

### 4.1.1 Why Agent-Based Modeling for the Negev Highlands?

The Iron Age IIA oscillation in the Negev Highlands requires moving beyond static spatial analysis toward dynamic simulation. While Chapter 3 identified clustering patterns and environmental associations, it cannot address how individual household decisions, repeated over decades in a volatile environment, accumulate into the observed archaeological palimpsest.

Agent-Based Modeling (ABM) suits this problem because the archaeological record represents accumulated anecdotal moments-individual decisions about camp placement, enclosure construction, and crisis response-rather than a snapshot of contemporaneous occupation (Lake 2020; Romanowska et al. 2021; Lake 2014). Alternative approaches prove inadequate: statistical models like regression or MaxEnt are fundamentally static, treating the archaeological record as fixed outcomes of fixed predictors, unable to capture temporal processes or feedback loops between human activity and environmental degradation **\[CITE: Critique of static spatial models in archaeology - e.g., Kohler & van der Leeuw, or methodological paper on dynamic modeling\]**. Moreover, explicit computational models and especially ABM, force researchers to specify assumptions precisely and test their logical consequences (Romanowska et al. 2019), thus providing useful tool for hypothesis testing.

The model tests whether the refined nomadic development hypothesis proposed from spatial analysis can, when simulated with temporal dynamics, generate observed patterns. The hypothesis proposes that observed signatures result from palimpsest formation-repeated occupation of environmentally attractive areas by mobile populations across 75-100 years rather than contemporaneous operation (see above). This temporal cycling was driven by the region's environmental instability, where moving southeast correlates with decreasing stability (Bruins 2012). Households could not repeatedly occupy the same locations without risking environmental degradation or experiencing insufficient rainfall seasons, necessitating flexible adaptation strategies.

This observation challenges traditional assumptions that stone-built sites represent permanent occupation (Cohen 1979; Haiman 1992; Faust 2006; Rothenberg 1967; Shahack-Gross and Finkelstein 2008), proposing instead that sites may have functioned as seasonal facilities used for a few years before abandonment and potential later reuse. Testing this requires simulating annual household decision-making over multi-decadal timescales. The model enables "experiments", technically impossible in archaeology (Romanowska et al. 2019; Lake 2020), by systematically varying conditions to evaluate which factors critically shaped the archaeological record and whether the nomadic development hypothesis provides sufficient explanation. Despite inevitable parameter uncertainty and equifinality limitations inherent to all modelling approaches, it is believed that ABM can help us differentiate between plausible scenarios and complete unrealistic ones (Lake 2020; Crema 2018).

### 4.1.2 Research Questions Addressed by the Model

The model aspires to answer the question: _"Can autochthonous nomadic processes, operating through temporal cycling and environmental feedbacks, sufficiently generate pattern similar to the observed Iron Age IIA archaeological record?"_ This central question addresses whether the refined nomadic development can produce the spatial clustering and site-type diversity documented archaeologically. Critically, the model evaluates sufficiency rather than necessity: demonstrating that the refined hypothesis _can_ generate observed patterns does not prove it is the only explanation, but establishes its plausibility as an interpretive framework for understanding Iron Age IIA nomadic societies in the Negev Highlands (Lake 2014).

### 4.1.3 Model Scope and Limitations

The model represents a 3,251.54 km² portion of the Negev Highlands as a 318×280 grid of 250m cells, simulating 75 years of annual household movement cycles. It includes environmental variables (e.g. vegetation, agriculture, rainfall, water sources, terrain), household agents managing livestock and other resources, and processes of location selection, territory establishment, prosperity accumulation, and enclosure construction. The temporal scope represents the approximate duration of the Negev Highlands Iron Age IIA socio-economic system, with annual repositioning reflecting seasonal mobility patterns as proposed in the hypothesis.

Several limitations constrain the interpretive power of the model. Survey bias in the archaeological dataset affects spatial coverage, though Chapter 3's bias assessment provides controls. Environmental reconstructions remain uncertain due to limited paleoclimatic data for this specific period and region, requiring reliance on modern analogues, which are also missing for the Egyptian part of the region and therefore is not modelled. Since the parameter values lack direct empirical justification, the model demonstrates what parameter combinations can produce observed patterns but cannot determine "true" historical values without additional archaeological evidence.

The model necessarily simplifies complex social processes. Households function as unitary decision-making agents without modelling internal gender dynamics, age structures, or intra-household conflicts that undoubtedly influenced real site locations, size and occupation length. Environmental processes employ simplified degradation functions rather than detailed ecological models, as these require significant modelling effort, unavailable at a work of this scope. Stochasticity means individual model runs vary, requiring multiple replications to characterize typical outcomes. Also the model cannot, and does not aspire to determine actual site chronologies, distinguish between equifinal alternative explanations, or test other hypotheses (like the fortress model) excluded from its design assumptions.

Despite these constraints, the model provides insights unattainable through static spatial analysis: it demonstrates how temporal cycling and environmental feedbacks plausibly generate palimpsest patterns, reveals sensitivity to key parameters, and shows mechanisms by which autochthonous nomadic processes could produce the observed archaeological record.

## 4.2 Model Structure and Components

### 4.2.1 Spatial Representation of the Negev Highlands

The model represents the Negev Highlands as a discrete two-dimensional grid comprising 318×280 cells, each 250m×250m in size (6.25 hectares), yielding a total modeled area of 3,251.54 km². This spatial resolution balances computational efficiency with the need to capture meaningful environmental heterogeneity while accommodating known constraints in the archaeological and environmental datasets. The 250m cell size aligns with several practical considerations: the spatial accuracy of archaeological survey coordinates (approximately 100-500m positional error most surveys), the dispersed nature of Iron Age IIA sites themselves (with architectural remains sometimes distributed across 400m within a single site), and the resolution limitations of available environmental datasets.

The model extent follows the natural topographic boundaries of the Negev Highlands where possible, defined primarily by elevation and geomorphological characteristics that distinguish this highland region from surrounding desert lowlands. However, a significant methodological constraint shapes the western boundary: the modern Israel-Egypt border delimits the modeled area rather than the natural extent of the Negev Highlands. This boundary was imposed due to the absence of comparable environmental datasets for the Egyptian portion of the region, resulting in the exclusion of 48 archaeological sites (9.4% of the total Iron Age IIA dataset) from spatial pattern evaluation. Figure \[X\] presents the relationship between the model extent and both the full geographic extent of the Negev Highlands and the distribution of archaeological sites, illustrating this data-driven limitation.

The model employs bounded rather than toroidal space, meaning households cannot "wrap around" from one edge to appear at the opposite edge as often is the case in spatial ABMs (Lake 2020). To minimize edge effects while maintaining computational efficiency, the model includes a buffer zone extending beyond the valid placement boundaries. Environmental processes (degradation, resource calculation) operate across this extended area, but household agents cannot establish camps in the buffer zone. This design prevents artificial boundary effects in environmental calculations for households positioned near the modeled extent.

All spatial data are projected in the Israel Transverse Mercator (ITM) coordinate system, maintaining consistency with the archaeological survey records and ensuring accurate distance calculations for movement costs and territorial interactions. distinguished between **permanent parameters** that remain constant throughout simulations (mean annual rainfall, slope characteristics, distance to Tel el-Qudeirat, proximity to permanent water sources, and natural movement corridors) and **annual parameters** that update each year to represent temporal environmental variability (pasture vegetation suitability, agricultural potential, seasonal rainfall patterns, and available pasture). This dual temporal structure allows the model to capture both the stable geographic constraints and the dynamic environmental conditions that characterize arid marginal landscapes (detailed in Section 4.2.3). A binary "place raster" defines valid placement areas, effectively restricting agent activity to the Israeli portion of the Negev Highlands where environmental data coverage permits reliable modeling.

The spatial structure accommodates 75 years of annual household repositioning through dynamic environmental feedback mechanisms. As households occupy and degrade areas, the spatial distribution of suitable locations continuously shifts, driving the temporal cycling patterns central to the nomadic development hypothesis. While households can exhaust suitable unclaimed locations in any given year, the annual environmental updates and degradation recovery ensure that spatial opportunities remain dynamic rather than static, reflecting the environmental volatility characteristic of arid marginal landscapes.

### 4.2.2 Household Agents: Properties and Behaviours

Household agents represent the fundamental decision-making units in the model, corresponding to extended family groups consisting of approximately 10 nuclear families cooperating as a single economic and social entity. This conceptualization is adapted from Rosen and Finkelstein's (1992) estimates of pastoral carrying capacity in the Negev Highlands, which suggested approximately 36 livestock units per person within family units of roughly 6 individuals, but without being involved in copper production or trade, hence the model uses 18 livestock units per person to reflect the diversified economic base. Each household agent thus represents a cooperative group of 50-60 individuals managing collective resources and making coordinated decisions about camp placement, resource allocation, and infrastructure investment.

Household agents are characterized by three primary state variables representing their economic viability and decision-making capacity. **Livestock holdings** (measured as individual goats) constitute the household's primary productive asset, with herd sizes determined stochastically at initialization based on ethnographic expectations for pastoral groups in marginal environments. The model tracks livestock demographics across four age-sex categories (juvenile males, adult males, juvenile females, adult females) following proportions and valuations documented in Dahl and Hjort (1976:96) and Günther et al. (2021), enabling realistic representation of herd management strategies under resource stress. **Manpower** quantifies the number of working-age individuals available for herding, movement, and construction activities, directly constraining the household's capacity to exploit resources and invest in permanent structures. **Resource surplus** represents accumulated abstract resource units derived from livestock production, opportunistic agriculture, and participation in copper trade networks, functioning as the household's buffer against environmental uncertainty and the basis for prosperity-driven decisions.

Beyond these economic variables, households maintain two distinct memory systems that structure their spatial decision-making. **Personal encampment memory** stores location-specific information about past camping experiences, including environmental quality and year of use, with this knowledge decaying over time as older experiences become less relevant. **Collective enclosure memory** operates at the household level, preserving knowledge of previously constructed or encountered enclosed compounds across a broader spatial extent, representing inter-generational transmission of knowledge about permanent infrastructure locations. Both memory systems influence annual placement decisions but operate at different spatial and temporal scales, reflecting the distinction between individual experience and collective knowledge.

Each household also maintains a **personalized suitability raster** that augments the global environmental suitability surface with location-specific experience, weighting recent personal encounters more heavily than distant memories. This individualized landscape perception enables households to develop distinct spatial strategies even within shared environments, contributing to heterogeneity in spatial behaviour.

Household agents engage in four primary behavioural domains explored in detail in subsequent sections: **annual repositioning** whereby households select new camp locations each year based on environmental suitability, past experience, and territorial competition (Section 4.3.1); **resource management** involving livestock population dynamics, surplus calculation, and consumption decisions (Section 4.3.2); **prosperity-based enclosure construction** where sufficiently prosperous households invest in permanent infrastructure (Section 4.3.3); and **crisis response** through strategic livestock culling and territorial adjustment when resources fall below survival thresholds (Section 4.3.5). These behaviours emerge from households evaluating their economic state against environmental conditions, generating the spatial and organizational patterns that characterize the archaeological record.

The archaeological basis for household conceptualization reflects the challenge of inferring social organization from mobile pastoral societies where residential structures were often ephemeral. The model's extended family groups approximate the cooperative units necessary for managing substantial livestock herds in marginal environments while maintaining sufficient flexibility for seasonal mobility between the Negev Highlands and Arabah valley copper production zones.

### 4.2.3 Environmental Variables and Resources

The model integrates environmental variables through a two-tier classification system distinguishing between anthropogenic versus ecological parameters, each separated for permanent versus annual parameters (Figure \[X from presentation\]). This hierarchical structure enables the model to capture both stable geographic constraints and dynamic temporal variability characteristic of arid marginal environments, while accounting for human impacts on landscape suitability.

**Permanent Environmental Parameters**

Permanent environmental variables remain constant throughout simulations, representing stable geographic and climatic characteristics of the Negev Highlands. These include mean annual rainfall derived from Israeli Meteorological Service (IMS) station data through inverse distance weighting (IDW) interpolation, slope calculated from [JAXA ALOS PALSAR](https://doi.org/10.5067/Z97HFCNKR6VA) digital elevation model (12.5m resolution), proximity to arable soils (Pleistocene loess deposits and Hatzeva Formation sandy soils identified through Israeli Geological Survey maps), distance to permanent water sources (springs and wells compiled from topographic maps and other sources), and vegetation type distributions affecting pastoral carrying capacity (Danin 1966, Deshe 2024).

All distance-based parameters employ cost-distance calculations incorporating topographic influences on travel time, using Tobler's hiking function to convert terrain into walking hours (citation). Each permanent parameter undergoes fuzzy membership transformation to normalize values to a 0-10 suitability scale, enabling summation despite disparate original units. For example, slope suitability employs a FuzzySmall algorithm (midpoint=15°, spread=3) assigning maximum suitability to flat terrain, while mean annual rainfall uses linear fuzzy transformation (minimum=0mm, maximum=100mm) where values exceeding 100mm achieve maximum suitability. Distance to permanent water sources similarly applies small fuzzy transformation (midpoint=3 hours walking time, spread=1), reflecting diminishing suitability with increasing distance while acknowledging that adequate water accessibility exists throughout most of the Negev Highlands rather than competitive positioning around scarce resources.

**Annual Environmental Parameters**

Annual parameters introduce temporal variability through stochastic selection of environmental conditions for each simulated year. The primary driver is annual rainfall, randomly selected from observed years (August-July) measured by IMS stations, with years containing at least 20 active stations eligible for selection to ensure spatial coverage reliability. Selected annual rainfall maps undergo IDW interpolation and linear fuzzy normalization identical to permanent rainfall processing. Annual rainfall varies dramatically (approximately 30-160mm, citation), creating substantial inter-annual heterogeneity in resource availability.

Annual rainfall drives two derivative parameters representing seasonal resource availability. Available pasture combines vegetation type suitability with annual rainfall through multiplicative interaction, reflecting that pastoral productivity depends on both plant community composition and seasonal precipitation. Fertile arable soils emerge through zonal statistics calculating total rainfall within each loess/Hatzeva Formation polygon, with areas exceeding threshold values (???) classified as seasonally cultivable and subjected to cost-distance analysis. These annual agricultural and pastoral resources capture the opportunistic exploitation strategies characteristic of mobile populations in precipitation-limited environments.

**Permanent Anthropogenic Parameters**

Distance to Tel el-Qudeirat undergoes cost-distance calculation and small fuzzy transformation (midpoint=4 hours, spread=1) identical to permanent water source processing, reflecting hypothesized central place functions within the seasonal movement circuit.

**Dynamic Anthropogenic Variables**

Two dynamic anthropogenic factors emerge from accumulated human activity across simulation years: multi-annual resource exhaustion and reuse of previously built sites. Multi-annual exhaustion accumulates environmental degradation from past years through weighted summation where recent impacts receive higher weights, subsequently smoothed through spatial convolution (focal statistics) creating impact zones extending beyond immediate occupation locations. Reuse potential increases at locations of past encampments and especially enclosed compounds, with recent constructions weighted more heavily than older ones. These dynamic variables capture temporal cycling mechanisms central to the nomadic development hypothesis, where repeated occupation creates heterogeneous landscapes of opportunity and degradation driving annual repositioning decisions.

**Suitability Integration**

Overall environmental suitability combines weighted parameters through linear summation:

$$S_{total} = \sum_{i=1}^{n} W_i \cdot P_i$$

where calibrated weights $(W_i)$ determine relative parameter importance (Section 4.6). Parameters included in this summation are: proximity to Tel el-Qudeirat, proximity to permanent water sources, mean annual rainfall, slope, reuse of previously built sites, multi-annual resource exhaustion, and annual rainfall. Notably, proximity to arable soils and available pasture are excluded from the suitability calculation because both derive from annual rainfall; including them would overrepresent this base environmental resource.

All environmental layers are resampled to the model's 250m resolution and normalized to 0-10 scales through fuzzy membership functions (see [ARCGIS documentation](https://pro.arcgis.com/en/pro-app/3.3/tool-reference/spatial-analyst/fuzzy-membership.htm)), with transformation parameters tailored to each variable's relationship with settlement suitability. This preprocessing ensures computational compatibility while preserving meaningful variation across the heterogeneous Negev Highlands landscape.

### 4.2.4 Time Scales: Annual Cycles and Multi-Year Dynamics

The model employs a temporal resolution of one year per time step, with simulations running for 75 years to approximate the Iron Age IIA socio-economic system's duration in the Negev Highlands (c. 980-830 BCE) **\[CITE: Ben-Yosef et al. 2021; earlier chapter discussion\]**. This timeframe represents a minimal approximation; the actual duration could have been somewhat longer without fundamentally altering the model's processes.

Each annual time step represents the summer season when households occupy the Negev Highlands within the hypothesized seasonal movement pattern between the Arabah valley (winter) and Negev Highlands (summer). Agent "removal" from the grid at each year's end represents departure to the Arabah, while "relocation" at the beginning represents return to the region. This annual repositioning-where households select new camp locations based on updated environmental conditions, accumulated experience, and territorial competition-generates the model's spatial dynamics.

Within each time step, sub-processes execute sequentially: environmental variables update; households reposition based on suitability calculations; territories are established and resources calculated; prosperity assessments drive enclosure construction decisions; livestock populations and demographics adjust; and environmental degradation accumulates. This sequential execution creates cascading effects where environmental conditions influence placement, which determines resource acquisition, which drives prosperity and construction investments, which modify future suitability through degradation feedbacks.

The 75-year structure enables palimpsest formation-the central mechanism of the nomadic development hypothesis. Households repeatedly occupy and abandon locations across annual cycles, with each year contributing to cumulative archaeological signatures. Environmentally favourable areas experience repeated visits generating dense archaeological concentrations without contemporaneous occupation, while marginal areas receive only occasional use producing sparse signatures. The final output represents accumulated spatial footprint of dynamic occupation rather than simultaneous site operation, paralleling how the archaeological record preserves centuries of non-contemporaneous activity as apparently synchronous site distributions.

## 4.3 Agent Decision-Making and Behaviours

### 4.3.1 Location Selection Mechanisms

Household location selection operates through a probabilistic algorithm that integrates environmental suitability, accumulated experience, territorial constraints, and stochastic variation. This mechanism creates the conditions under which temporal cycling patterns could emerge, forming a core component of the nomadic development hypothesis being tested.

**Initial Placement and Annual Repositioning**

Location selection differs between model initialization and subsequent annual cycles. During Year 1, households position themselves based solely on environmental suitability - the weighted sum of permanent and annual parameters described in Section 4.2.3. Selection is probabilistic: each cell's selection probability equals its suitability value cubed and normalized across all valid areas. The cubic transformation amplifies differences between moderately and highly suitable locations, creating strong preferences for optimal areas while maintaining stochastic variation that prevents unrealistic competition for identical spaces.

From Year 2 onward, households augment environmental suitability with personal experience, creating individualized landscape perceptions. These personalized evaluations incorporate territorial attachment to previously occupied areas and memory of past camping experiences. Each household thus develops distinct spatial preferences even within shared environments, contributing to heterogeneity in activity patterns.

**Experience-Based Suitability Modification**

Households modify base environmental suitability through two additive adjustments. Territorial attachment operates through distance decay: cells within or near the previous year's territory receive suitability bonuses inversely proportional to distance from territory boundaries (up to 10 cells beyond), calculated as $bonus = \frac{k}{d + 1}$. This captures spatial inertia observed in pastoral systems where households preferentially return to familiar areas absent compelling reasons to relocate \[CITE: ethnographic examples of pastoral territorial attachment\].

Memory adjustments apply location-specific modifications based on past occupation quality. Each household stores previous camp locations, experienced environmental quality, and occupation year. Memory influences future placement through time-weighted adjustments decaying hyperbolically as $w = \frac{1}{(T - t) + 1}$, with recent experiences weighing more heavily than distant memories \[CITE: cognitive psychology of spatial memory or ethnographic pastoral examples\].

Memory effects vary by experience quality. Locations with favourable conditions (environmental quality ≥5 on 0-10 scale) receive positive suitability adjustments, encouraging return visits. Locations with marginal conditions (quality <5) suffer negative adjustments, discouraging immediate reuse. Critically, locations occupied in the current year receive fixed penalties regardless of quality, preventing immediate reoccupation and forcing annual movement. Memory persistence incorporates stochastic decay, with individual memories having variable lifespans averaging 5-10 years, reflecting imperfect intergenerational knowledge transmission.

**Territorial Competition**

After probabilistic location selection, households evaluate whether their potential territory, a 20-30 cell radius around the selected position, varying with local environmental quality, conflicts with existing territories. A 25% overlap threshold applies: if more than one-quarter of proposed territory cells already belong to other households, the location is rejected and selection repeats. This prevents extreme territorial compression while allowing some flexibility reflecting shared resource use in marginal pastoral environments \[CITE: commons usage in pastoral systems\].

Households select positions sequentially in random order each year, creating path dependence where early-positioning households secure preferred locations while later households choose from remaining areas. During environmental downturns or after multi-year degradation accumulation, competition intensifies, and marginal areas receive increased use.

**Mechanisms Enabling Palimpsest Formation**

These location selection rules create conditions under which the hypothesized palimpsest formation could occur. Environmental degradation from past occupation reduces suitability at previously used locations, while memory-based avoidance discourages immediate return. These mechanisms enable households to cycle through the landscape, potentially revisiting favourable areas across multi-year intervals rather than permanently occupying them. Territorial competition distributes households across available suitable space, while probabilistic selection generates both patterning and variation.

### 4.3.2 Resource Management and Surplus Calculation

Household economic viability depends on managing three interconnected resources: livestock herds, manpower (workforce), and accumulated surplus. Resource management operates through a two-stage annual process: first calculating surplus from current productive capacity, then adjusting livestock populations based on environmental conditions and needs, with stochastic events introducing variability reflecting the unpredictable challenges of arid marginal environments.

**Livestock Productivity and Surplus Generation**

Households manage goat herds initialized around 105 goats (used as representative for all livestock) per nuclear family unit (approximately 1,050 animals per household; adapted from Rosen and Finkelstein 1992). The model tracks herd demographics through four general age-sex categories following proportions documented in literature, with differential productivity values reflecting their economic roles (Dahl and Hjort 1976:96; Günther et al. 2021): juvenile males (14.8%, value 0.3), adult males (8.8%, value 0.4), juvenile females (18.5%, value 0.25), and adult females (57.9%, value 0.2).

Annual surplus generation converts livestock productivity into abstract resource units from animals exceeding subsistence requirements, calculated as $manpower \times 18$ animals per person adjusted for environmental stress. Livestock productivity responds to environmental carrying capacity evaluated within a 25-cell radius, where medium-quality pasture (5 on 0-10 scale) supports 1.125 goats per 250m cell. When herd size exceeds local carrying capacity, stress accumulates through additional maintenance costs (15% of herd size × stress ratio), reducing surplus generation.

Agricultural potential within household territories reduces livestock subsistence requirements by up to 40%, enabling more livestock productivity to be converted into surplus (Rosen and Finkelstein 1992; Günther et al. 2021). Copper trade participation appears implicitly through reduced per-capita livestock requirements, acknowledging additional economic resources without explicitly modelling trade mechanics.

**Consumption, Stochastic Events, and Surplus Dynamics**

Households face baseline consumption needs: 0.8 surplus units per person for non-subsistence expenses, plus communal costs calculated as 30% of manpower representing social obligations. Annual stochastic scenarios introduce unpredictable challenges: adverse scenarios (25% probability) increase communal costs 30-60% and potentially reduce herds 5-12% through disease, conflict, or harsh weather; neutral scenarios (50% probability) apply normal consumption; favourable scenarios (25% probability) reduce costs 10-30% and occasionally provide small bonuses. These events operate independently from environmental quality effects, representing social and epidemiological variability rather than landscape-driven resource availability.

Surplus persists across years but decays 30% annually representing resource spoilage and gradual consumption. Households maintaining large surpluses (>50 units) face additional progressive decay (5-40%) reflecting storage difficulties and social redistribution pressures, creating diminishing returns that prevent indefinite accumulation.

**Annual Herd Dynamics**

Following surplus calculation, livestock populations adjust based on environmental conditions. When resources exceed requirements (carrying capacity/herd size >1.1), herds grow up to 10% annually with diminishing returns as herds approach 1,000 animals. When resources fall short (ratio <0.9), herds decline 10-30% depending on resource scarcity. Small herds (<500 animals) receive enhanced recovery factors, representing emergency preservation strategies.

### 4.3.3 Prosperity-Based Enclosure Construction

Enclosure construction represents households' strategic investment in permanent infrastructure when economic conditions permit, operationalizing the hypothesis that stone-built compounds reflect temporal resources availability rather than sedentary occupation. The model implements multi-stage decision-making where households first assess prosperity, then evaluate existing enclosures for potential reuse, and finally consider new construction if conditions warrant investment.

Prosperity assessment combines economic capacity and environmental quality:

$$P = \frac{surplus + manpower + environmental\_quality}{3}$$

Households achieving prosperity index >0.7 become eligible for enclosure-related investments. Actual construction requires substantially higher criteria: reusing existing enclosures demands manpower ≥15 and surplus exceeding baseline threshold, while constructing new enclosures requires prosperity index >0.8, manpower ≥40, and surplus three times baseline threshold. These escalating requirements ensure only genuinely prosperous households in favorable conditions invest in permanent structures.

Prosperous households first search for existing enclosures within their territory. The search prioritizes the household's own previous constructions (built within 20 years), then considers all landscape enclosures built within 15 years at lower priority (80% weighting). Environmental factors modify selection probabilities, with enclosures in locations having higher vegetation and agricultural values receiving enhanced scores. Stochastic variation (±20%) introduces probabilistic selection rather than deterministic choice. When suitable enclosures exist and thresholds are met, households reuse structures at reduced cost (10 manpower, 6 surplus). This represents practical strategies of returning to familiar locations with existing infrastructure.

If no suitable enclosures exist, households select construction locations based on environmental quality, preferentially choosing sites exceeding territorial mean suitability. Recent enclosures (within 25 years) are excluded to prevent clustering. Construction costs (20 manpower, 25 surplus) represent significant investment, depleting accumulated surplus but establishing infrastructure that enhances future spatial attachment.

Enclosures persist throughout simulations without decay, though reuse probability declines with abandonment duration. Individual households may construct multiple enclosures across 75 years but occupy only one annually. Occupying enclosures increases spatial inertia in subsequent location selection through enhanced territorial attachment and memory effects. This generates activity patterns where prosperous households repeatedly visit and renovate specific locations across multi-year intervals, producing archaeological signatures of substantial stone architecture at environmentally favourable sites without requiring permanent occupation.

### 4.3.4 Territory Establishment and Competition

Territory establishment structures household annual spatial claims and resource access, creating the framework for competitive interactions that distribute households across the landscape. The model implements cooperative territorial relationships without explicit conflict, using spatial overlap constraints to represent negotiated coexistence among mobile pastoral groups.

**Territory Definition and Environmental Responsiveness**

Immediately following location selection, households establish territories as Moore neighbourhoods centred on camp positions (Moore neighbourhoods reference). Territory size responds to local environmental quality of standard 20-cells radius neighbourhood: poor conditions (mean quality <3.5 on 0-10 scale) trigger expansion to 30-cell radius, moderate conditions (3.5-5.0) produce 25-cell radius, and favourable conditions (>5.0) maintain base 20-cell radius. This adaptive sizing represents pastoral ranging strategies where households exploit larger areas when resources are scarce \[CITE: ethnographic parallels for pastoral territory/ranging behavior\]. Territories persist for single annual cycles, resetting when households reposition each year.

**Overlap Constraints and Competition**

Territorial competition operates through passive exclusion. During location selection, incoming households evaluate potential territories for overlap with already-established territories. Positions where proposed territory would share more than 25% of cells with existing territories are rejected, forcing alternative location selection. This threshold represents practical modelling constraint balancing territorial tolerance in cooperative pastoral societies against spatial distribution requirements.

The overlap constraint applies asymmetrically: only incoming households face restrictions, while already-settled households retain territories regardless of subsequent arrivals. Sequential placement in randomized order creates path dependence where early-positioning households secure preferred locations and later households select from remaining areas. This generates emergent competitive dynamics without explicit conflict, matching archaeological evidence suggesting cooperative territorial relationships \[CITE: archaeological evidence for cooperation if available\].

**Resource Access and Environmental Feedbacks**

Territories define spatial extent for resource evaluation and environmental impact. Households assess agricultural potential and carrying capacity across entire territories, with mean values determining surplus generation. Environmental degradation extends across full territory radius (intensity 0.5, weight 0.9), representing grazing, firewood collection, and other extractive activities.

When territories overlap within the 25% limit, overlapping cells experience cumulative degradation from multiple households. This implements resource competition through environmental feedback rather than explicit conflict. Territory distribution emerges from interaction between environmental quality, overlap constraints, and sequential placement, producing dispersed patterns within preferred zones while directing households toward marginal areas when suitable locations become scarce.

### 4.3.5 Crisis Response and Survival Strategies

Households facing severe resource shortages engage strategic livestock culling to generate emergency surplus. These responses enable household persistence through environmental downturns while creating demographic turnover that maintains stable regional population levels.

**Crisis Response and Culling Hierarchy**

Crisis response activates when household surplus falls below 10 units, representing the minimum threshold necessary for household management. Households respond through strategic culling following demographically informed hierarchies (Dahl and Hjort 1976; Günther et al. 2021): juvenile males culled first (0.3 surplus units per animal), followed by adult males (0.4 units), then juvenile females (0.25 units, maximum 80% culled), and finally adult females as last resort (0.2 units, maximum 40% culled).

Culling targets escalating surplus thresholds reflecting household desperation: juvenile males aim for 100 units, adult males for 50 units, juvenile females for 25 units, and breeding females for the bare minimum 10 units. This sequence balances immediate survival against long-term herd viability. Households culling breeding females enter severe crisis mode, triggering territorial contraction to 15-cell radius, reflecting both reduced ranging needs for depleted herds and weakened competitive capacity.

**Household Extinction and Demographic Turnover**

Households fail when surplus falls below zero, livestock holdings drop below 15 animals, or manpower reaches zero. Failed households contribute residual resources to initialize replacement households created at year's end, maintaining stable regional population while generating turnover. Substantial turnover driven by sequential adverse years that trigger widespread crises.

Surviving households recover via normal herd growth mechanisms, with small depleted herds benefiting from enhanced growth rates. The model assumes regional persistence rather than permanent emigration, justified by archaeological evidence for population continuity and hypothesized attachment to unique Arabah copper resources \[CITE: archaeological evidence; Ben-Yosef on copper\].

## 4.4 Environmental Feedbacks and Degradation

### 4.4.1 Human Impact on Landscape Suitability

Human occupation degrades local environmental quality through two mechanisms operating at different spatial scales. When a household establishes its central yearly location, degradation affects cells within its territory radius (averaging 20 cells, approximately 5km; see Section 4.3.4). Nuclear family camps (Section 4.2.2) produce smaller-scale impacts within an 11-cell radius around their seasonal locations (see eq 4.x-x+1). Both mechanisms function identically in principle, differing only in magnitude: the degradation intensity decreases with distance from the occupation point according to an inverse-distance function, with the occupied cell itself experiencing the strongest impact. Suitability values are reduced but cannot fall below 0, preventing negative environmental values.

These immediate degradation effects operate within a single year. After each household or nuclear family placement, the model updates the suitability raster, ensuring that subsequent location decisions by other agents account for recently degraded areas. This creates dynamic competition for high-quality locations within each annual cycle, as early-placing households affect the landscape available to those placing later.

**Equations 4.x and 4.x+1: Distance-based environmental degradation from household and nuclear family occupation.**

$$S'(x,y) = \max\left(S(x,y) - D \cdot \frac{1}{d(x,y) + 1}, 0.0001\right)$$

$$S'(center) = \max(S(center) \cdot (1 - P), 0.0001)$$

Where $S'(x,y)$ is the updated suitability at cell $(x,y)$, $S(x,y)$ is the original suitability, $D$ is the degradation factor, $d(x,y)$ is Manhattan distance from the occupied cell, and $P$ is the position degradation factor for the center cell. Households use $D = 0.5$ and $P = 0.9$; nuclear family camps use $D = 0.3$ and $P = 0.5$. Minimum suitability is 0.0001.

Beyond immediate impacts, the model tracks inter-annual cumulative degradation through occupation intensity records. Each year's occupation pattern contributes to a weighted accumulation that spans multiple years. Recent occupation exerts stronger influence than older occupation, implementing an implicit recovery process: cells occupied in the previous year have had less time to recover than those last visited five or ten years ago. The temporal decay factor of 0.7 means degradation influence diminishes exponentially with time since occupation (eq 4.x+2).

**Equation 4.3: Temporal decay weighting for inter-annual degradation.**

$$w(t) = 0.7^{(T-t)}$$

Where $w(t)$ is the weight applied to occupation in year $t$, $T$ is the current year, and $(T-t)$ is years since occupation. The decay factor of 0.7 weights recent occupation more heavily, implementing implicit landscape recovery over time.

Cumulative degradation effects also diffuse spatially beyond the cells directly occupied. Using inverse-distance weighting over a 5km radius, the model spreads degradation pressure across neighbouring areas, representing processes such as grazing impacts that extend beyond immediate campsites. This spatial smoothing creates broader zones of reduced suitability around repeatedly occupied areas rather than isolated degraded points.

The accumulated degradation translates into a stress multiplier that integrates into annual suitability calculations alongside environmental variables such as rainfall and slope. High cumulative stress reduces location attractiveness, influencing both household placement and resource management decisions. Degradation thus feeds back into carrying capacity calculations and pastoral productivity, creating conditions where intensively used areas become progressively less suitable until occupation pressure shifts elsewhere.

This degradation system does not deterministically force temporal cycling, but makes it more plausible. A location occupied last year suffers reduced suitability, though exceptionally favourable rainfall years can offset degradation effects and permit reoccupation. The mechanism creates spatial patchiness in occupation patterns as households distribute across the landscape to avoid recently degraded areas, contributing to the palimpsest formation central to the nomadic development hypothesis.

\[CITE: General sources on pastoral environmental impacts and recovery rates in arid/semi-arid environments\]

### 4.4.2 Carrying Capacity Dynamics

Carrying capacity constrains household placement through an explicit location filter. During the placement algorithm (section 4.3.1), potential territories are evaluated for their ability to support household needs based on aggregated environmental suitability. Locations where calculated capacity falls below the household's requirements are rejected, effectively excluding environmentally insufficient areas from consideration regardless of other attractive characteristics. This mechanism ensures households only establish camps where basic resource thresholds can be met.

Beyond location selection, carrying capacity governs pastoral productivity through a dynamic feedback with environmental stress. The stress raster generated from cumulative occupation history (Section 4.4.1) directly reduces vegetation suitability, which in turn lowers pastoral carrying capacity. This creates conditions where intensive occupation degrades landscapes, reducing their ability to support livestock populations. When herds exceed local capacity, resource stress accumulates (Section 4.3.2), creating economic pressure that constrains household prosperity and livestock growth. The resulting spatial and temporal patchiness in carrying capacity reinforces cyclical occupation patterns as households must continuously respond to shifting resource availability across the landscape.

## 4.5 Model Implementation

### 4.5.1 Initialization Procedures

Model initialization establishes the environmental conditions and household population before the first simulated year, creating the starting state from which 75 years of temporal dynamics emerge (Figure 4.X).

Environmental initialization proceeds in three stages. First, permanent environmental rasters load from preprocessed GIS datasets (Table 4.x): mean annual rainfall, slope, proximity to arable soils, distance to permanent water sources, and distance to Tel el-Qudeirat. These static parameters remain constant throughout all 75 simulation years. Second, annual conditions for Year 0 are established by randomly selecting a historical rainfall year from available IMS records, ensuring initial environmental variability reflects realistic precipitation patterns. This selected rainfall year determines derived annual parameters including available pasture (vegetation suitability × annual rainfall) and seasonally cultivable agricultural areas. Third, dynamic anthropogenic layers initialize as zeros: the multi-annual exhaustion layer (tracking cumulative degradation across years) and the reuse potential layer (recording previous enclosure locations) contain no prior human impacts at initialization.

These environmental layers combine through weighted summation to generate the initial suitability raster following the calibrated parameter values described in Section 4.6.3. This initial suitability calculation differs from subsequent years in lacking memory-based or experience-based modifications, representing a purely environmental landscape assessment unmediated by prior occupation.

Household agent creation follows a conservative carrying capacity approach adapted from Rosen and Finkelstein's (1992) estimates for pastoral populations in the Negev Highlands. The model initializes nine household agents, calculated as:

$$N_{households} = \frac{3251.54 \text{ km}^2}{18 \text{ km}^2} \times 0.05 \approx 9$$

where the 18 km² denominator represents the spatial requirement per nuclear family unit (doubling the 9 km² baseline to account for marginal environment constraints), and the 0.05 factor reflects conservative occupation well below theoretical maximum capacity. This reduced starting population enables testing whether the nomadic development hypothesis can generate observed archaeological patterns even from modest initial conditions, avoiding assumptions about full landscape saturation.

Each household initializes with stochastically determined livestock holdings drawn from a normal distribution centred at approximately 1,050 goats (105 per nuclear family unit × 10 families per household), representing the productive asset base necessary for pastoral subsistence in arid environments (Dahl & Hjort 1976 on pastoral herd sizes; Rosen & Finkelstein 1992). Manpower calculations derive from livestock holdings through:

$$manpower = \max\left(\sqrt{\frac{livestock}{18}}, 5\right)$$

ensuring minimum viable workforce while scaling labor capacity to herd management requirements. All households begin with zero surplus, as Year 0 represents initial occupation before resource accumulation. The exception occurs only in subsequent years when replacement households inherit residual surplus from failed households, maintaining regional resource continuity despite demographic turnover.

Spatial placement proceeds sequentially in randomized order, with each household executing the location selection algorithm described in Section 4.3.1. Since Year 1 lacks accumulated experience, households select positions probabilistically based solely on environmental suitability, with selection probability proportional to suitability cubed. Following location selection, households immediately establish territories and position nuclear family camps within those territories using identical suitability-based probabilistic selection. Environmental degradation applies immediately after each household placement (Section 4.4.1), ensuring subsequent households in the placement sequence encounter landscapes already modified by earlier arrivals.

Initialization concludes with the model's first annual cycle: household decision-making processes run for Year 0, then environmental rasters update, and agent positions reset to transition into Year 0 of the simulation loop. This sequence ensures that by the time iterative annual cycles begin, households have established initial territories, accumulated first-year experiences, and modified the landscape through their occupation activities.

### 4.5.2 Annual Cycle Execution

Each simulated year (Years 0-74) executes through a two-phase cycle: household decision-making followed by environmental transition (Figure 4.Y). This structure separates agent behaviours from landscape updates, ensuring temporal consistency in how households respond to environmental conditions and how those responses modify future suitability.

The household decision-making phase processes all nine households in randomized order, preventing systematic advantages from consistent execution sequences. Each household executes its complete annual behavioural sequence: resource calculation and stochastic scenario application (Section 4.3.2), prosperity assessment and enclosure decisions (Section 4.3.3), crisis response if necessary (Section 4.3.5), followed by livestock adjustments, manpower demographic changes, and surplus decay. The randomized order creates path-dependent outcomes where early-acting households may secure optimal resources or locations before later households make their decisions.

Following all household actions, the model records agent states (manpower, livestock, surplus, position, enclosure memory) and spatial activity through the target raster tracking household positions during the year. These observations enable reconstruction of annual spatial distributions and demographic trajectories across the 75-year simulation.

The environmental transition phase then resets household grid positions and updates dynamic environmental layers for the upcoming year. Annual rainfall conditions are randomly selected from historical records, driving recalculation of pastoral and agricultural resources. Multi-annual exhaustion incorporates the previous year's degradation through weighted temporal accumulation (Section 4.4.1), while reuse potential updates with newly constructed enclosures. The suitability raster recalculates from these revised parameters using calibrated weights (Section 4.6.3).

Household repositioning completes the transition phase. Each household's memory undergoes stochastic pruning, retaining experiences where $(current\_year - memory\_year) \times random\_value < 5$. Households then execute location selection (Section 4.3.1) using personalized suitability rasters incorporating updated environmental conditions and retained memories. Territory establishment follows, nuclear family members position within territories, and environmental degradation applies immediately, completing the cycle.

The simulation terminates after Year 74's household decision-making phase without executing a final environmental transition, preserving the last year's spatial configuration for pattern analysis.

## 4.6 Model Calibration and Validation

### 4.6.1 Calibration Strategy: Pattern-Oriented Modelling

Model calibration employed Pattern-Oriented Modelling (POM), a multi-criteria framework specifically designed for agent-based models where complex system-level patterns emerge from low-level individual processes (Grimm et al. 2005; Grimm and Railsback 2012). This approach addresses a fundamental challenge in testing the nomadic development hypothesis: demonstrating that simulated household decisions about camp placement, resource management, and enclosure construction can generate archaeological patterns similar to those observed in the Iron Age IIA Negev Highlands.

**Rationale for Pattern-Oriented Modelling**

POM differs fundamentally from traditional statistical calibration approaches in its emphasis on structural realism rather than mere statistical fit (Grimm and Railsback 2012). Where conventional methods might calibrate models to reproduce single aggregate measures, POM requires models to simultaneously match multiple patterns observed at different organizational levels and spatial scales. This multi-pattern constraint addresses the problem of equifinality, where many different model structures or parameter combinations could reproduce any single pattern, but far fewer can reproduce multiple independent patterns simultaneously (Gallagher et al. 2021).

For testing the nomadic development hypothesis, POM provides critical advantages. The hypothesis proposes that observed archaeological signatures result from decentralized household decision-making operating through temporal cycling and environmental feedbacks across 75-100 years. Testing this requires demonstrating that low-level behavioural processes (annual location selection, prosperity-based enclosure construction, crisis responses) produce higher-level spatial and organizational outcomes (regional settlement distribution, site-type differentiation) that match archaeological observations. POM explicitly tests this micro-macro linkage by simultaneously constraining models at both individual and system levels (Gallagher et al. 2021; Grimm and Railsback 2012).

The approach aligns with POM's core strategy of ensuring models reproduce patterns "for the right reasons" (Gallagher et al. 2021). Rather than imposing archaeological patterns through model rules, the calibration process identifies parameter combinations that enable emergent pattern formation through simulated household behaviours. If the model can generate observed patterns only through mechanisms consistent with the nomadic development hypothesis, this provides evidence for the hypothesis's plausibility as an explanatory framework.

**Pattern Selection and Weighting**

Calibration targeted two patterns derived from the archaeological record (detailed in Section 4.6.2): spatial distribution of all sites measured through standard deviational ellipse overlap, and site-type ratios comparing enclosed compounds to other sites. These patterns were selected for their diagnostic power in testing the hypothesis while avoiding patterns that would require predicting exact site locations, which falls outside the model's scope given inherent uncertainties in archaeological chronology and survey coverage.

Spatial distribution patterns capture the regional-scale organization emerging from accumulated household placement decisions across 75 simulated years. Standard deviational ellipses characterize not only where sites concentrate but also the orientation and extent of those concentrations, providing spatially explicit assessment without requiring point-to-point correspondence. This pattern tests whether simulated temporal cycling through environmentally suitable areas generates archaeological palimpsest signatures matching observed distributions.

Site-type ratios address a key prediction of the nomadic development hypothesis: that enclosed compounds represent prosperity-driven infrastructure investment by successful households rather than functionally distinct site categories imposed by external authorities. The ratio of enclosed compounds to other sites therefore tests whether the model's prosperity calculation and enclosure construction mechanisms (Section 4.3.3) generate appropriate frequencies of substantial stone architecture within the simulated nomadic system.

Both patterns received equal weighting in the calibration objective function. This decision reflects their complementary diagnostic value: spatial distribution tests whether households cycle through the landscape in archaeologically plausible ways, while site-type ratios test whether prosperity accumulation and investment decisions occur at appropriate frequencies. Weighting patterns equally prevents the calibration from optimizing one pattern at the expense of the other, maintaining balance between spatial and organizational criteria.

Alternative pattern choices were deliberately excluded. Location-specific metrics such as kernel density estimation or nearest-neighbor distances would require the model to predict exact site positions, inappropriate given that individual household decisions are stochastic and that archaeological survey coverage varies across the region (Chapter 3, Appendix 2). The selected patterns instead evaluate whether the model generates the correct type and scale of spatial organization without demanding unrealistic precision about specific locations.

**Calibration Scope and Parameter Selection**

Calibration focused exclusively on the seven environmental suitability weights referenced in Section 4.2.3: distance to Tel el-Qudeirat, proximity to permanent water sources, mean annual rainfall, slope suitability, return to previously occupied sites, multi-annual human stress, and annual rainfall. These weights determine how environmental factors combine to influence household location selection, making them the primary controls on emergent spatial patterns. All seven weights were calibrated simultaneously rather than sequentially, allowing the optimization process to identify synergistic combinations that improve pattern matching across both target patterns.

Other model parameters remained fixed based on archaeological evidence, ethnographic analogues, or theoretical considerations established during model development. For example, livestock demographics follow proportions documented in pastoral literature (Dahl and Hjort 1976; Günther et al. 2021), prosperity thresholds derive from logical requirements for infrastructure investment, and degradation functions reflect general principles of environmental impact in arid pastoral systems. Fixing these parameters focuses calibration on the environmental preference structure while acknowledging that multiple aspects of household behaviour rest on empirical or theoretical foundations independent of the specific Negev Highlands case.

**Addressing Equifinality and Model Credibility**

The POM approach explicitly acknowledges rather than ignores equifinality. Multiple parameter combinations may produce similar pattern matches, reflecting genuine uncertainty about precise environmental preferences within the historical nomadic system. The calibration process identifies parameter sets capable of reproducing observed patterns but does not claim to determine "true" historical values. This aligns with the model's purpose of testing sufficiency rather than necessity: demonstrating that the nomadic development hypothesis can generate observed patterns establishes its plausibility, while acknowledging that alternative explanations might also be viable (Lake 2014).

By requiring simultaneous reproduction of two independent patterns observed at different scales, the calibration substantially constrains the parameter space compared to single-pattern approaches. Parameter sets that might reproduce spatial distributions through mechanisms inconsistent with appropriate site-type ratios, or vice versa, are eliminated during optimization. This multi-pattern constraint builds confidence that acceptable parameter combinations represent mechanisms consistent with the underlying hypothesis rather than achieving pattern matches through inappropriate processes.

### 4.6.2 Target Patterns from Archaeological Record

Model calibration targeted two quantitative patterns derived from the Iron Age IIA archaeological record of the Negev Highlands: the spatial distribution of all sites and the ratio of enclosed compounds to other site types. These patterns provide complementary constraints on model behaviour, with spatial distribution testing emergent regional organization and site-type ratios testing the frequency of prosperity-driven infrastructure investment. Full documentation of archaeological data collection, site classification, and pattern measurement appears in Chapter 3; this section summarizes the patterns used as calibration targets.

**Spatial Distribution Pattern**

The spatial distribution pattern characterizes the regional extent, orientation, and centroid of Iron Age IIA occupation through standard deviational ellipse analysis applied to 462 archaeological sites within the model boundaries (Chapter 3). This method captures approximately 95% of site locations within a two-standard-deviation ellipse, providing spatially explicit assessment of where activity concentrates without requiring exact site position predictions.

The observed archaeological pattern exhibits a standard deviational ellipse covering 1,585.02 km² with centroid at coordinates 168,369.37 E, 515,592.33 N (ITM grid). The ellipse orientation follows a northwest-southeast axis (major axis 66.68 km at 55.66°, minor axis 30.26 km), yielding an elongation ratio of 2.2:1. This elongated distribution reflects concentration of Iron Age IIA activity along the main elevated plateau of the Negev Highlands, with the southeast orientation aligning with the hypothesized seasonal movement corridor between Tel el-Qudeirat and the Arabah valley copper production zones.

The displacement between mean center (168,369.37 E, 515,592.33 N) and median center (168,223.20 E, 512,622.45 N) of approximately 3.0 km toward the south-southwest suggests slight clustering in the southern portion of the distribution. This spatial organization forms the first calibration target: simulated household placement decisions operating through 75 annual cycles should generate accumulated activity patterns with similar regional extent, orientation, and centroid location as observed archaeologically.

**Site-Type Ratio Pattern**

The site-type ratio quantifies the frequency of enclosed compounds relative to other architectural site types within the archaeological dataset. Of the 462 sites analysed within model boundaries, 32 sites (6.93%) contain enclosed compounds characterized by stone-built oval, rectangular, or irregular enclosures with casemate walls and central courtyards (Chapter 3). The remaining 425 sites (93.07%) represent other architectural forms including circular structures, rectangular buildings, towers, and four-room houses, occurring individually or in combinations. Five additional sites exhibited questionable enclosure characteristics and were excluded from this analysis, yielding a conservative enclosed compound count.

This observed ratio of approximately 1:13.3 (enclosed compounds to other sites) forms the second calibration target. The nomadic development hypothesis proposes that enclosed compounds represent prosperity-driven infrastructure investment by successful households rather than functionally distinct site categories, predicting that enclosure construction should occur with moderate frequency reflecting the subset of households achieving sufficient surplus and favourable environmental conditions to warrant permanent investment (Section 4.3.3). Calibration therefore targets parameter combinations enabling the model to generate enclosed compound frequencies similar to archaeological observations.

**Pattern Measurement and Uncertainties**

Both target patterns were measured from the archaeological database described in Chapter 3, which compiled site data primarily from Israel Antiquities Authority survey records supplemented by legacy surveys (Glueck 1958; Aharoni et al. 1960; Rothenberg 1967). The dataset necessarily reflects survey coverage patterns, with some areas more intensively documented than others (Chapter 3, Appendix 2). While distance-to-road analysis indicates modest proximity bias in surveyed areas, assessment demonstrates that survey coverage does not substantially alter broader regional spatial trends analysed in calibration.

A fundamental asymmetry exists between observed and simulated patterns. The archaeological record represents a partial palimpsest: accumulated evidence of activities occurring across 75-100 years that has survived differential preservation, variable survey coverage, and post-depositional processes. Some sites may remain undiscovered, architectural remains may have eroded, and the chronological precision necessary to determine which sites operated contemporaneously versus sequentially remains unattainable. In contrast, the simulated pattern represents complete information about all household positions and enclosure constructions at the moment activity ceases (Year 74), capturing the full system state without preservation or discovery biases.

This asymmetry means calibration cannot demand exact pattern reproduction. Rather, calibration identifies parameter combinations enabling the model to generate patterns sufficiently similar to archaeological observations that differences could plausibly result from preservation and survey biases rather than fundamental mechanistic inadequacies. The standard deviational ellipse approach accommodates this by evaluating regional-scale organization rather than site-specific predictions, while the site-type ratio assessment tolerates reasonable variation around observed frequencies given uncertainties in both archaeological classification and stochastic model outcomes.

### 4.6.3 Parameter Optimization Methods

Parameter optimization employed Optuna (Akiba et al. 2019), a hyperparameter optimization framework designed for efficiently exploring large discrete and continuous parameter spaces through adaptive sampling strategies. The optimization targeted seven environmental suitability weights controlling how household agents evaluate potential camp locations: distance to Tel el-Qudeirat, proximity to permanent water sources, mean annual rainfall, slope suitability, return to previously occupied sites, multi-annual human stress, and annual rainfall. These weights combine through linear summation to generate the environmental suitability raster that drives household location selection (Section 4.2.3), making them the primary controls on emergent spatial patterns.

**Parameter Search Space and Representation**

Each of the seven weights was parameterized as a discrete integer ranging from 0 to 7, creating eight ordinal importance levels for each environmental factor. This discretization serves two purposes. First, discrete integer spaces substantially reduce computational search space compared to continuous parameters: seven continuous parameters would require exploring infinite combinations, while seven discrete parameters with eight levels each define a finite (though still very large) search space of $8^7 = 2,097,152$ possible combinations. Second, the ordinal scale provides intuitive importance categorization where 0 represents exclusion of that factor, low values (1-2) indicate minor influence, moderate values (3-5) suggest intermediate importance, and high values (6-7) denote dominant factors. This representation balances exploratory flexibility with computational tractability.

The seven discrete weights function not as independent parameters but as relative importance values normalized to sum to 1 before application. During each optimization trial, sampled integer values are summed and then divided by that sum, converting raw integers into proportional weights. For example, if sampled values were [3, 0, 5, 2, 1, 4, 6], they would normalize to [0.143, 0.000, 0.238, 0.095, 0.048, 0.190, 0.286]. This normalization ensures that weights represent relative environmental preferences rather than absolute scaling factors, preventing the search from exploring arbitrary magnitude combinations while maintaining interpretable importance rankings.

The environmental parameters calibrated through these weights represent factors directly incorporated into the suitability calculation. Parameters manifested indirectly through other variables were excluded from calibration to avoid redundancy. For example, agricultural suitability derives from the interaction between soil types and annual rainfall, making separate calibration of agricultural parameters unnecessary given that annual rainfall weights are optimized. Similarly, pasture availability emerges from vegetation type and annual rainfall interactions, eliminating need for independent pasture weighting.

**Objective Function Structure**

The objective function quantifies model-data fit by combining two pattern similarity measures into a composite score that Optuna minimizes. For each parameter combination, the function executes ten replicate simulations with identical parameters but different random seeds, accounting for stochasticity in household decisions, environmental variability, and demographic events. Each replicate generates a simulated spatial distribution (household positions accumulated over 75 years) and site-type composition (counts of sites with and without enclosed compounds).

Pattern similarity assessment proceeds through two parallel calculations (Figure 4.X). Spatial distribution similarity employs standard deviational ellipse overlap analysis comparing simulated and observed site distributions. Both datasets undergo ellipse calculation capturing 95% of points (two standard deviations), yielding ellipse area, centroid location, major and minor axes, and orientation angle. The spatial similarity component quantifies overlap through:

$$overlap\_metric = \frac{A_{overlap}}{A_{overlap} + A_{non-overlap}}$$

Where $A_{overlap}$ represents area shared by both ellipses and $A_{non-overlap}$ represents non-overlapping areas. This metric ranges from -1 (complete separation) through 0 (equal overlap and non-overlap) to 1 (perfect overlap). The spatial similarity score converts this to:

$$spatial\_score = 1 - overlap\_metric$$

yielding values from 0 (perfect match) to 2 (maximum dissimilarity).

Site-type ratio similarity compares the proportion of sites containing enclosed compounds between simulated and observed datasets. The observed archaeological pattern exhibits 32 enclosed compounds among 462 total sites (6.93% or ratio of 0.0693), while simulated patterns vary stochastically depending on household prosperity dynamics and construction decisions. The ratio similarity component calculates:

$$ratio\_score = \left| \frac{simulated\_enclosures}{simulated\_total} - 0.0693 \right|$$

This absolute difference quantifies how far the simulated enclosure frequency deviates from archaeological observations, with 0 indicating perfect match and larger values indicating increasing discrepancy.

The composite objective score averages these two components:

$$total\_score = \frac{spatial\_score + ratio\_score}{2}$$

This equally weighted combination treats spatial distribution and site-type ratios as co-equal constraints, reflecting their complementary diagnostic value established in Section 4.6.1. Optuna seeks parameter combinations minimizing this total score, simultaneously improving both pattern matches. For each parameter combination, the ten replicate total scores are averaged using simple arithmetic mean, providing a single objective value that accounts for stochastic variation while avoiding sensitivity to individual outlier runs.

**Optimization Algorithm and Sampling Strategy**

Optuna employed the Tree-structured Parzen Estimator (TPE) sampler for adaptive parameter space exploration (Watanabe 2023). TPE constructs probabilistic models of promising versus unpromising regions of parameter space based on previous trial outcomes, concentrating subsequent sampling in areas likely to yield improved objective scores. A MedianPruner terminated trials early when intermediate results indicated unlikely improvement over previous trials, reducing computational waste on unpromising parameter combinations. These algorithmic choices balance exploration of diverse parameter combinations against exploitation of promising regions, enhancing optimization efficiency within computational constraints.

**Exploratory Calibration and Formal Optimization**

Prior to formal optimization, exploratory calibration involved manual parameter testing to develop intuition about model sensitivity and reasonable parameter ranges. These initial runs served to verify that the model could produce qualitatively plausible outputs, identify parameters with strong versus weak effects on pattern matching, and debug technical implementation issues before committing computational resources to systematic optimization. Exploratory runs revealed, for example, that annual rainfall weights required substantial influence to generate appropriate temporal cycling, while some parameters initially considered (but later excluded as redundant) contributed minimal additional pattern-matching capability.

Formal optimization executed [PLACEHOLDER] trials, each involving ten replicate simulations. With individual runs requiring approximately two minutes, single trials consumed roughly 20 minutes, and full optimization demanded substantial computational investment ([PLACEHOLDER] total hours). This computational constraint motivated the discrete parameter representation and algorithmic efficiency measures described above. The large search space (over 2 million possible discrete combinations) precludes exhaustive exploration, making adaptive sampling strategies essential for identifying high-quality parameter sets within feasible computational budgets.

Optimization terminated after completing the predetermined [PLACEHOLDER] trials rather than employing convergence criteria. This fixed-trial approach ensures reproducible optimization procedures while acknowledging that global optima may remain undiscovered given the vast parameter space and stochastic objective function. The best parameter combination identified through [PLACEHOLDER] trials provides a parameter set enabling pattern reproduction consistent with the nomadic development hypothesis, though alternative parameter combinations with similar performance may exist.

### 4.6.4 Validation Results: Model-Data Comparison (REPORTING)

### 4.6.5 Goodness-of-Fit Metrics (REPORTING)

## 4.7 Sensitivity Analysis

### 4.7.1 Parameters Tested

### 4.7.2 Effects on Spatial Distribution

### 4.7.3 Effects on Site Type Ratios

### 4.7.4 Robustness Assessment

## 4.8 Simulation Experiments

### 4.8.1 Experimental Design

### 4.8.2 Baseline Scenario (Calibrated Model)

### 4.8.3 Alternative Scenarios

- Varying environmental conditions
- Different economic priorities
- Altered prosperity thresholds

### 4.8.4 Comparison with Archaeological Patterns (REPORTING scenarios comparison)

## 4.9 Model Results and Interpretation (all discussion/interpretation)

### 4.9.1 Emergent Settlement Patterns (INTERPRETATION of mechanisms)

### 4.9.2 Temporal Dynamics and Palimpsest Formation

### 4.9.3 Testing the Nomadic Development Hypothesis

### 4.9.4 Insights into Enclosure Function and Distribution
