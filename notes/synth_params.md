
## Ways to sample a synthesizer from presets
* Parse preset file and make correspondence to MIDI
* Construct FXB from preset file?

### MIDI params
* Easy to obtain list of parameters for random sampling
* Parameter list is incomplete

### FXB
* Chunk may be scrambled/unparseable
* Would still need to parse FXB for something

## type of parameters 

### Categorical
* List every possible value (treat as str) [0, 1, "On"]
* For MIDI: Each str corresponds to what value in MIDI ("Square:0.4")
* Takes integer from min-max (0-9)

### Continuous
* Just range (min value and max value)

## Param info
* name
* type (continuous, categorical, unknown)
* range
* If there is one, Corresponding MIDI param name
    - Param correspondence

# Getting parameters from presets
* Parsing preset file
    - Needs a manual program for each format
* Loading from fxb then getting MIDI params
    - Still needs to convert MIDI to meaningful format (with param type) to use properly in inference
    - Only for parameters with MIDI

## Convert to MIDI compatible format?
* Easy for continuous var

* Idea: load fxb and check correspondence between midi values?

## Plan A (Current flow)
Preset file -> Parse **params** -> params to midi -> Set params by MIDI -> **audio**
* can't deal with non MIDI Params
* random sampling is easy

## Plan B
Preset file -> Parse **params**
            -> Construct FXB -> Set params by FXB -> **audio**
* might be harder to fix certain parameters and move certain ones
* FXB construction is murky (possible for Diva)