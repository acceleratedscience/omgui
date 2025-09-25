<sub>[&larr; BACK](../)</sub>

# OMGUI - `chartviz` - Chart Visualization

![chartviz sub-module](https://img.shields.io/badge/sub--module-omgui.chartviz-yellow)

The `chartviz` sub-module lets you visualize various types of data charts on the fly, either as HTML page, SVG or PNG.

Note that the chart & [molecule](molviz.md) visualization requires additional dependencies:

```shell
pip install git+https://github.com/themoenen/omgui.git@v0.1[viz]
```

![Chart visualization with omgui.chartviz](assets/chart-preview.svg)

### Supported Chart Types

See [examples](#examples) below.

-   bar charts
-   line charts
-   pie charts
-   scatter plots
-   bubble charts
-   box plots
-   histograms

<br>

## Instructions

In order to use the chart visualization, simply start the server in the background, then compose your url:

`/viz/chart/<chart_type>?data=<your_data>&output=<svg/png>`

```python
import omgui

omgui.launch()
```

```text
http://localhost:8024/viz/chart/boxplot?data=%5B%7B%22name%22%3A%22Lion%22%2C%22data%22%3A%5B0.515771883018405%2C0.3375953434817889%2C0.5070375838802724%2C0.5204925268901693%2C0.015091552731013147%2C0.6318510844035372%2C0.3731448444453114%2C0.4841547079732992%2C0.6569717889886966%2C0.4616403565481917%5D%2C%22groups%22%3A%5B%22A%22%2C%22A%22%2C%22A%22%2C%22A%22%2C%22B%22%2C%22B%22%2C%22B%22%2C%22C%22%2C%22C%22%2C%22C%22%5D%7D%2C%7B%22name%22%3A%22Tiger%22%2C%22data%22%3A%5B0.6182350648761221%2C0.3411718466411763%2C0.7278257988670094%2C0.3346028267346215%2C0.11012489893918775%2C0.786575449649989%2C0.41678789600410904%2C0.8021970313587021%2C0.24470456348949854%2C0.8200487945865108%5D%2C%22groups%22%3A%5B%22A%22%2C%22A%22%2C%22A%22%2C%22A%22%2C%22B%22%2C%22B%22%2C%22B%22%2C%22C%22%2C%22C%22%2C%22C%22%5D%7D%2C%7B%22name%22%3A%22Elephant%22%2C%22data%22%3A%5B0.8402424213441659%2C0.5469183665936138%2C0.15056426355569785%2C0.5539100254096991%2C0.12217771096918395%2C0.02421208318587509%2C0.020432894158663895%2C0.3258277585944509%2C0.2459912916673579%2C0.5197551920892144%5D%2C%22groups%22%3A%5B%22A%22%2C%22A%22%2C%22A%22%2C%22A%22%2C%22B%22%2C%22B%22%2C%22B%22%2C%22C%22%2C%22C%22%2C%22C%22%5D%7D%2C%7B%22name%22%3A%22Giraffe%22%2C%22data%22%3A%5B0.7956089534725999%2C0.5975432461927672%2C0.9775939452894175%2C0.9907505165083172%2C0.9521782296971075%2C0.5109890977478964%2C0.06769003664698514%2C0.9442911399395388%2C0.8792575232225094%2C0.11018984624953354%5D%2C%22groups%22%3A%5B%22A%22%2C%22A%22%2C%22A%22%2C%22A%22%2C%22B%22%2C%22B%22%2C%22B%22%2C%22C%22%2C%22C%22%2C%22C%22%5D%7D%5D
```

### Demo Interface

Use the demo interface to see what options are available, how to compose your URL and how to structure your data for each type of chart.

http://localhost:8024/viz/chart

![chartviz demo UI](assets/chartviz-demo-ui.png)

<br>

## Deployment

Because the chart visualization depends on some system requirements for the Plotly PNG/SVG output to work, it's recommended to deploy it using Docker or Podman, as the [Dockerfile](Dockerfile) takes care of installing these dependencies. See `apt-get` and `plotly_get_chrome`.

<br>

## Examples

![Example chart: Line chart](assets/chart-example-line.svg)
![Example chart: Box plot](assets/chart-example-box-plot.svg)
![Example chart: Scatter chart](assets/chart-example-scatter-plot.svg)
![Example chart: Histogram](assets/chart-example-histogram.svg)
![Example chart: Bar chart](assets/chart-example-bar.svg)
![Example chart: Bubble chart](assets/chart-example-bubble.svg)
![Example chart: Pie chart](assets/chart-example-pie.svg)

<!--
```python
from omgui import chartviz

groups = ["Group A", "Group B", "Group C"]
data = [
    {
        "keys": groups,
        "name": "Flamingo",
        "data": [ 56, 79, 10 ]
    },
    {
        "keys": groups,
        "name": "Possum",
        "data": [ 81, 10, 50 ]
    },
    {
        "keys": groups,
        "name": "Shrew",
        "data": [ 99, 20, 45 ]
    }
]

chartviz.boxplot(data)
```
-->
