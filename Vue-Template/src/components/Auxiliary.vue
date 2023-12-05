<script lang="ts">
import * as d3 from "d3";
// import Data from '../../data/demo.json'; /* Example of reading in data directly from file */
import axios from "axios";
import { isEmpty, debounce } from "lodash";
import Data from "../../data/temp_data_s50.json";

import {
  Bar,
  ComponentSize,
  Margin,
  Pos,
  Range,
  ScatterPlot,
  SelectedRegions,
  BarChart,
} from "../types";
// A "extends" B means A inherits the properties and methods from B.
interface CategoricalBar extends Bar {
  category: string;
}

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram

export default {
  data() {
    // Here we define the local states of this component. If you think the component as a class, then these are like its private variables.
    return {
      bars: [] as CategoricalBar[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
      size: { width: 0, height: 0 } as ComponentSize,
      margin: { left: 60, right: 20, top: 20, bottom: 60 } as Margin,
      indexes_to_plot: [] as Pos[],
      data_scatter_plot: [] as ScatterPlot[],
      temp_range: { max: 0, min: 0 } as Range,
      OH_range: { max: 0, min: 0 } as Range,
      current_selected_regions: {} as SelectedRegions,
      selected_slice: 0 as number,
      data_bar_chart: [] as BarChart[],
    };
  },
  computed: {
    // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
    rerender() {
      return !isEmpty(this.data_scatter_plot) && this.size;
    },
  },
  // Anything in here will only be executed once.
  // Refer to the lifecycle in Vue.js for more details, mentioned at the very top of this file.
  created() {
    // fetch the data via GET request when we init this component.
    // In axios anything we send back in the response are always bound to the "data" property.
    /*
        axios.get(`<some-API-endpoint>`)
            .then(resp => { 
                this.bars = resp.data; // resp.data contains the content, with the format specified by the API you use.
                return true;
            })
            .catch(error => console.log(error));
        */
    console.log(Data);
    if (isEmpty(Data)) return;
    // this.bars = Data.data;
    // for (let i = 0; i < Data.vox_grid[this.selected_slice].length; i++) {
    //   this.data_scatter_plot.push({
    //     temp: Data.vox_grid[this.selected_slice][i],
    //     OH: Data.OH_grid[this.selected_slice][i],
    //   });
    // }
    this.selected_slice = 0;
    this.current_selected_regions.layerIDs = [1];
    this.current_selected_regions.componentIDs = [
      1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    ];
    this.current_selected_regions.cellIDs = [1189, 1195];
    this.current_selected_regions.cellIDs = [60, 69, 78, 86, 88];

    this.collectScatterPlotValues(0);
    this.collectBarChartValues(2);

    // this.layer_thresh = Data.layer_thresh[selected];
    // this.cmpt_thresh = Data.component_thresh[selected];
    // this.cell_thresh = Data.cell_thresh[selected];

    // this.layer_grid = Data.layer_grid[selected];
    // this.cmpt_grid = Data.component_grid[selected];
    // this.cell_grid = Data.cell_grid[selected];

    this.temp_range = {
      max: Math.max(...Data.vox_grid[this.selected_slice]),
      min: Math.min(...Data.vox_grid[this.selected_slice]),
    };
    this.OH_range = {
      max: Math.max(...Data.OH_grid[this.selected_slice]),
      min: Math.min(...Data.OH_grid[this.selected_slice]),
    };
  },
  methods: {
    onResize() {
      // record the updated size of the target element
      let target = this.$refs.barContainer as HTMLElement;
      if (target === undefined) return;
      this.size = { width: target.clientWidth, height: target.clientHeight };
    },
    collectScatterPlotValues(selected_level: number) {
      // collect the corresponding voxels' values
      let raw_data: any;
      let compared_data: any;
      if (selected_level == 0) {
        // layer part
        raw_data = Data.layer_grid[this.selected_slice];
        compared_data = this.current_selected_regions.layerIDs;
      } else if (selected_level == 1) {
        // component part
        raw_data = Data.component_grid[this.selected_slice];
        compared_data = this.current_selected_regions.componentIDs;
      } else if (selected_level == 2) {
        // cell part
        raw_data = Data.cell_grid[this.selected_slice];
        compared_data = this.current_selected_regions.cellIDs;
      }
      raw_data.forEach((ID, i) => {
        compared_data.forEach((match) => {
          if (ID == match) {
            this.data_scatter_plot.push({
              temp: Data.vox_grid[this.selected_slice][i],
              OH: Data.OH_grid[this.selected_slice][i],
            });
          }
        });
      });
    },
    collectBarChartValues(selected_level: number) {
      let raw_data: any;
      let compared_data: any;
      if (selected_level == 0) {
        // layer part
        raw_data = Data.layer_grid[this.selected_slice]
        compared_data = this.current_selected_regions.layerIDs
      } else if (selected_level == 1) {
        // component part
        raw_data = Data.component_grid[this.selected_slice]
        compared_data = this.current_selected_regions.componentIDs
      } else if (selected_level == 2) {
        // cell part
        raw_data = Data.cell_grid[this.selected_slice]
        compared_data = this.current_selected_regions.cellIDs
      }
      compared_data.forEach((match) => {
          let arr_temp: number[] = [];
          let arr_OH: number[] = [];
          raw_data.forEach((layerID, i) => {
            if (layerID == match) {
              arr_temp.push(Data.vox_grid[this.selected_slice][i]);
              arr_OH.push(Data.OH_grid[this.selected_slice][i]);
            }
          });
          this.data_bar_chart.push({
            id: match,
            voxCount: arr_temp.length,
            meanTemp: Number(d3.mean(arr_temp) ? d3.mean(arr_temp) : 0),
            meanOH: Number(d3.mean(arr_OH) ? d3.mean(arr_OH) : 0),
            stdTemp: Number(
              d3.deviation(arr_temp) ? d3.deviation(arr_temp) : 0
            ),
            stdOH: Number(d3.deviation(arr_OH) ? d3.deviation(arr_OH) : 0),
          });
        });
    },
    scatterPlot() {
      // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
      let chartContainer = d3.select("#bar-svg2");

      let x = d3
        .scaleLinear()
        .domain([this.temp_range.min, this.temp_range.max])
        .range([this.margin.left, this.size.width - this.margin.right]);

      chartContainer
        .append("g")
        .attr(
          "transform",
          `translate(0, ${this.size.height / 2 - this.margin.bottom})`
        )
        .call(d3.axisBottom(x));

      let y = d3
        .scaleLinear()
        .domain([this.OH_range.min, this.OH_range.max])
        .range([this.size.height / 2 - this.margin.bottom, this.margin.top]);

      chartContainer
        .append("g")
        .attr("transform", `translate(${this.margin.left}, 0)`)
        .call(d3.axisLeft(y));

      const xLabel = chartContainer
        .append("g")
        .attr(
          "transform",
          `translate(${this.size.width / 2}, ${
            this.size.height / 2 - this.margin.bottom + 30
          })`
        )
        .append("text")
        .text("Temperature values")
        .style("font-size", ".8rem");

      const yLabel = chartContainer
        .append("g")
        .attr(
          "transform",
          `translate(${this.margin.left - 50}, ${
            this.size.height / 4
          }) rotate(-90)`
        )
        .append("text")
        .text("OH values")
        .style("font-size", ".8rem");

      chartContainer
        .append("g")
        .selectAll("dot")
        .data(this.data_scatter_plot)
        .enter()
        .append("circle")
        .attr("cx", function (d) {
          return x(d.temp);
        })
        .attr("cy", function (d) {
          return y(d.OH);
        })
        .attr("r", 1.5)
        .style("fill", "#69b3a2");

      const title = chartContainer
        .append("g")
        .append("text") // adding the text
        .attr(
          "transform",
          `translate(${this.size.width / 2}, ${
            this.size.height / 2 - this.margin.bottom + 40
          })`
        )
        .attr("dy", "0.5rem") // relative distance from the indicated coordinates.
        .style("text-anchor", "middle")
        .style("font-weight", "bold")
        .text("Temperature/OH of Voxels in Selected Regions (i.e. Layer 1)"); // text content

      let cnt = d3
        .select("#count")
        .html("debug (plot points count): " + this.data_scatter_plot.length);
    },
    barChart() {
      let chartContainer = d3.select("#bar-svg3");

      let yMin = Number(
        d3.min(
          this.data_bar_chart.map(
            (d: BarChart) => (d.meanTemp - d.stdTemp) as number
          )
        )
      );
      let yMax = Number(
        d3.max(
          this.data_bar_chart.map(
            (d: BarChart) => (d.meanTemp + d.stdTemp) as number
          )
        )
      );

      d3.extent(
        this.data_bar_chart.map((d: BarChart) => d.meanTemp as number)
      ) as [number, number];
      let xCategories: string[] = [
        ...new Set(
          this.data_bar_chart.map((d: BarChart) => String(d.id) as string)
        ),
      ] as string[];

      let xScale = d3
        .scaleBand()
        .rangeRound([this.margin.left, this.size.width - this.margin.right])
        .domain(xCategories)
        .padding(0.1); // spacing between the categories

      // In viewport (our screen), the topmost side always refer to 0 in the vertical coordinates in pixels (y).
      let yScale = d3
        .scaleLinear()
        .range([this.size.height / 2 - this.margin.bottom, this.margin.top]) //bottom side to the top side on the screen
        .domain([yMin < 0 ? yMin : 0, yMax]);

      console.log("check: " + yScale.domain()[1]);

      const xAxis = chartContainer
        .append("g")
        .attr(
          "transform",
          `translate(0, ${this.size.height / 2 - this.margin.bottom})`
        )
        .call(d3.axisBottom(xScale));

      const yAxis = chartContainer
        .append("g")
        .attr("transform", `translate(${this.margin.left}, 0)`)
        .call(d3.axisLeft(yScale));

      const xLabel = chartContainer
        .append("g")
        .attr(
          "transform",
          `translate(${this.size.width / 2}, ${
            this.size.height / 2 - this.margin.bottom + 30
          })`
        )
        .append("text")
        .text("Layer/Component/Cell Ids")
        .style("font-size", ".8rem");

      const yLabel = chartContainer
        .append("g")
        .attr(
          "transform",
          `translate(${this.margin.left - 50}, ${
            this.size.height / 4
          }) rotate(-90)`
        )
        .append("text")
        .text("Mean and Standard Deviation")
        .style("font-size", ".8rem");

      // create error bar shape
      function erro_bar(d: any) {
        let p = d3.path();
        let shrink: number = xScale.bandwidth() / 4;
        // Vertical line
        p.moveTo(
          Number(xScale(String(d.id))) + xScale.bandwidth() / 2,
          Number(yScale(d.meanTemp - d.stdTemp))
        );
        p.lineTo(
          Number(xScale(String(d.id))) + xScale.bandwidth() / 2,
          Number(yScale(d.meanTemp + d.stdTemp))
        );
        // Bottom error bar
        p.moveTo(
          Number(xScale(String(d.id))) + shrink,
          Number(yScale(d.meanTemp - d.stdTemp))
        );
        p.lineTo(
          Number(xScale(String(d.id))) + xScale.bandwidth() - shrink,
          Number(yScale(d.meanTemp - d.stdTemp))
        );
        // Top error bar
        p.moveTo(
          Number(xScale(String(d.id))) + shrink,
          Number(yScale(d.meanTemp + d.stdTemp))
        );
        p.lineTo(
          Number(xScale(String(d.id))) + xScale.bandwidth() - shrink,
          Number(yScale(d.meanTemp + d.stdTemp))
        );
        return p.toString();
      }

      // A function that change this tooltip when the user hover a point.
      // Its opacity is set to 1: we can now see it. Plus it set the text and position of tooltip depending on the datapoint (d)
      let showTooltip = function (event, d) {
        console.log("hover: " + tooltip.property("offsetWidth"));
        tooltip.transition().duration(100).style("opacity", 1);
        tooltip
          .html(
            "id: " +
              d.id +
              "<br>mean: " +
              d.meanTemp +
              "<br>std: " +
              d.stdTemp +
              "<br>voxel number: " +
              d.voxCount
          )
          .style("left", event.x - tooltip.property("offsetWidth") / 2 + "px")
          .style("top", event.y - tooltip.property("offsetHeight") - 10 + "px");
      };
      let moveTooltip = function (event, d) {
        tooltip
          .style("left", event.x - tooltip.property("offsetWidth") / 2 + "px")
          .style("top", event.y - tooltip.property("offsetHeight") - 10 + "px");
      };
      // A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
      let hideTooltip = function (event, d) {
        tooltip.transition().duration(100).style("opacity", 0);
      };

      const barchart = chartContainer
        .append("g")
        .selectAll("rect")
        .data<BarChart>(this.data_bar_chart) // TypeScript expression. This always expects an array of objects.
        //.join('rect')
        .join("rect")
        // specify the left-top coordinate of the rectangle
        .attr("x", (d: BarChart) => xScale(String(d.id)) as number)
        .attr("y", (d: BarChart) => yScale(d.meanTemp) as number)
        // specify the size of the rectangle
        .attr("width", xScale.bandwidth())
        .attr("height", (d: BarChart) =>
          Math.abs(yScale(yScale.domain()[0]) - yScale(d.meanTemp))
        ) // this substraction is reversed so the result is non-negative
        .attr("fill", "#ADD8E6")
        .on("mouseover", showTooltip)
        .on("mousemove", moveTooltip)
        .on("mouseleave", hideTooltip);

      const error_bars = chartContainer
        .append("g")
        .selectAll("path")
        .data<BarChart>(this.data_bar_chart)
        .join("path")
        .attr("d", erro_bar)
        .style("fill", "none")
        .style("stroke", "#000000")
        .style("opacity", 1.0);

      const title = chartContainer
        .append("g")
        .append("text") // adding the text
        .attr(
          "transform",
          `translate(${this.size.width / 2}, ${
            this.size.height / 2 - this.margin.bottom + 40
          })`
        )
        .attr("dy", "0.5rem") // relative distance from the indicated coordinates.
        .style("text-anchor", "middle")
        .style("font-weight", "bold")
        .text("Statistics from Layers/Components/Cells (i.e. cells)"); // text content

      let tooltip = d3
        .select("#root")
        .append("div")
        .attr("id", "tooltip")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("background-color", "black")
        .style("color", "white")
        .style("border-radius", "5px")
        .style("padding", "10px")
        .style("font-size", "10px")
        .style("position", "absolute");
    },
  },
  watch: {
    rerender(newSize) {
      if (!isEmpty(newSize)) {
        d3.select("#bar-svg2").selectAll("*").remove(); // Clean all the elements in the chart
        this.scatterPlot();

        d3.select("#tooltip").remove();

        d3.select("#bar-svg3").selectAll("*").remove(); // Clean all the elements in the chart
        this.barChart();
      }
    },
  },
  // The following are general setup for resize events.
  mounted() {
    window.addEventListener("resize", debounce(this.onResize, 100));
    this.onResize();
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.onResize);
  },
};
</script>

<!-- "ref" registers a reference to the HTML element so that we can access it via the reference in Vue.  -->
<!-- We use flex (d-flex) to arrange the layout-->
<template>
  <p id="count"></p>
  <div class="chart-container d-flex" ref="barContainer">
    <v-col id="root">
      <svg id="bar-svg2" width="100%" height="50%">
        <!-- all the visual elements we create in scatterPlot() will be inserted here in DOM-->
      </svg>
      <svg id="bar-svg3" width="100%" height="50%"></svg>
    </v-col>
  </div>
</template>

<style scoped>
.chart-container {
  height: 100%;
}
</style>

