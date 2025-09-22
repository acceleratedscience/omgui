# SPF

_Styled Printing and Feedback_

<sub>This module is part of [omgui](https://github.com/acceleratedscience/omgui)</sub>

Lightweight styling library to style/color text and dataframe output for the terminal, Jupyter Notebook and API.

Style text using XML-like tags like `<red>`, `<bold>`, `<underline>`, etc. These will then be converted to ANSI escape codes for terminal output,
to basic HTML for Jupyter Notebooks, and stripped out for API output.

Dataframes are displayed and paginated and with opinionated styling in the terminal.

<br>

## Core Methods

Both the main module and the table submodule have three core methods:

### Print

Print the styled text/table to the terminal or Jupyter Notebook cell.

```
spf(...)
spf.table(...)
```

### Produce

Return the styled text/table.

```
spf.produce(...)
spf.table.produce(...)
```

### Result

Print in terminal mode, return as Markdown/df in notebook mode and as plain text/JSON in api mode.  
This is useful for functions which may be called from either a script, Notebook or API.

```
return result(...)
return result.table(...)
```

<br>

## Usage

```
import spf

# Set the mode
# (optional, Notebook is auto-detected by default)
# ---
spf.set_mode("api") # terminal, notebook, api


# ------------------------------------
# Styling text
# ------------------------------------


# Simple styled print
# ---
spf("<cyan>Hello <bold>World</bold></cyan>")


# Success, warning and error messages
# ---
spf.success("Hello World") # green
spf.warning("Hello World") # yellow
spf.error("Hello World")   # red


# Returning styled text
# ---
x = spf.produce("Hello <bold>World</bold>")
print(x)


# ------------------------------------
# Tables
# ------------------------------------


# Print paginated table data
# ---
spf.table(df)

# Return table data for further processing
# ---
x = spf.table.produce(df)
print(x)


# ------------------------------------
# Returning results
# ------------------------------------


def get_text():
    text = ...
    return spf.result(text)

def get_data():
    df = ...
    return spf.table.result(df)
```
