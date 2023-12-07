<script lang="ts">
import * as d3 from "d3";
// import Data from '../../data/demo.json'; /* Example of reading in data directly from file */
import axios from "axios";
import { isEmpty, debounce } from "lodash";
import Data from "../../data/temp_data_s30.json";
import LevelDepInfo from "../../data/level_depen.json";

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
      temp_range: { max: 0, min: 0 } as Range,
      OH_range: { max: 0, min: 0 } as Range,
      current_selected_regions: {} as SelectedRegions,
      selected_slice: 0 as number,
      data_scatter_plot: [] as ScatterPlot[],
      data_bar_chart: [] as BarChart[],
      scatter_plot_showing_level: "" as string,
      bar_chart_showing_level: "" as string,
      current_level: -1 as number,
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
    // register for the event bus
    this.emitter.on("selected_info_passed", this.recieveParamsFromContours);
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
    //still need to let bar chart to show overview of current level
    this.current_selected_regions.layerIDs = [1, 2];
    this.current_selected_regions.componentIDs = [];
    this.current_selected_regions.cellIDs = [];
    this.current_level = 0;
    this.collectScatterPlotValues(0);
    this.collectBarChartValues(0);

    // this.layer_thresh = Data.layer_thresh[selected];
    // this.cmpt_thresh = Data.component_thresh[selected];
    // this.cell_thresh = Data.cell_thresh[selected];

    // this.layer_grid = Data.layer_grid[selected];
    // this.cmpt_grid = Data.component_grid[selected];
    // this.cell_grid = Data.cell_grid[selected];

    this.temp_range = {
      max: Math.max(...Data.vox_grid /*[this.selected_slice]*/),
      min: Math.min(...Data.vox_grid /*[this.selected_slice]*/),
    };
    this.OH_range = {
      max: Math.max(...Data.OH_grid /*[this.selected_slice]*/),
      min: Math.min(...Data.OH_grid /*[this.selected_slice]*/),
    };
  },
  methods: {
    recieveParamsFromContours(evt) {
      // click for reverse navigation
      if (evt.id_selected == -1) {
        // back to all components in selected layer
        if (this.current_level == 2) {
          // scatter plot for
          this.data_scatter_plot = [];
          this.collectScatterPlotValues(0);
          // bar chart for
          this.current_selected_regions.componentIDs = [];
          this.current_selected_regions.layerIDs.forEach((ele) => {
            for (
              let j = 0;
              j < LevelDepInfo.layers_components[ele].length;
              j++
            ) {
              this.current_selected_regions.componentIDs.push(
                LevelDepInfo.layers_components[ele][j]
              );
            }
          });
          this.data_bar_chart = [];
          this.collectBarChartValues(1);

          this.current_level = 1;
        }
        // back to all layers
        else if (this.current_level == 1) {
          // scatter plot for
          this.data_scatter_plot = [];
          this.current_selected_regions.layerIDs = [1, 2];
          this.collectScatterPlotValues(0);
          // bar chart for
          this.data_bar_chart = [];
          this.collectBarChartValues(0);

          this.current_level = 0;
        }
      }
      // select layer, show scater plot of this layer and bar chart of components in this layer
      else if (evt.level_selected == 0) {
        // for showing scatter plot
        this.current_selected_regions.layerIDs = [];
        this.current_selected_regions.layerIDs.push(evt.id_selected);
        // for showing bar chart
        this.current_selected_regions.componentIDs = [];
        for (
          let i = 0;
          i < LevelDepInfo.layers_components[evt.id_selected].length;
          i++
        ) {
          this.current_selected_regions.componentIDs.push(
            LevelDepInfo.layers_components[evt.id_selected][i]
          );
        }
        // scatter plot for layer
        this.data_scatter_plot = [];
        this.collectScatterPlotValues(0);
        // bar chart for component
        this.data_bar_chart = [];
        this.collectBarChartValues(1);

        this.current_level = 1;
      }
      // select component, show scatter plot of this component and bar chart of cells in this component
      else if (evt.level_selected == 1) {
        this.current_selected_regions.componentIDs = [];
        this.current_selected_regions.componentIDs.push(evt.id_selected);
        this.current_selected_regions.cellIDs = [];
        for (
          let i = 0;
          i < LevelDepInfo.components_cells[evt.id_selected].length;
          i++
        ) {
          this.current_selected_regions.cellIDs.push(
            LevelDepInfo.components_cells[evt.id_selected][i]
          );
        }
        // scatter plot for component
        this.data_scatter_plot = [];
        this.collectScatterPlotValues(1);
        // bar chart for cell
        this.data_bar_chart = [];
        this.collectBarChartValues(2);

        this.current_level = 2;
      }
      // select cells, show scatter plot of these cells and no change on bar chart
      // bug waited to be fixed (if have selected cells in cell level and db click to reverse navigation, it would notify event twice)
      // temporarily use evt.id_selected != "" to avoid it
      else if (evt.level_selected == 2 && evt.id_selected != "") {
        this.current_selected_regions.cellIDs = evt.id_selected;
        // scatter plot for component
        this.data_scatter_plot = [];
        this.collectScatterPlotValues(2);
        // no cleaning on data_bar_chart to remain the bar chart

        this.current_level = 2;
      }
      this.plotChart();
    },
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
        raw_data = Data.layer_grid /*[this.selected_slice]*/;
        compared_data = this.current_selected_regions.layerIDs;
        this.scatter_plot_showing_level = "Layer";
      } else if (selected_level == 1) {
        // component part
        raw_data = Data.component_grid /*[this.selected_slice]*/;
        compared_data = this.current_selected_regions.componentIDs;
        this.scatter_plot_showing_level = "Component";
      } else if (selected_level == 2) {
        // cell part
        raw_data = Data.cell_grid /*[this.selected_slice]*/;
        compared_data = this.current_selected_regions.cellIDs;
        this.scatter_plot_showing_level = "Cells";
      }
      raw_data.forEach((ID, i) => {
        compared_data.forEach((match) => {
          if (ID == match) {
            this.data_scatter_plot.push({
              temp: Data.vox_grid /*[this.selected_slice]*/[i],
              OH: Data.OH_grid /*[this.selected_slice]*/[i],
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
        raw_data = Data.layer_grid /*[this.selected_slice]*/;
        compared_data = this.current_selected_regions.layerIDs;
        this.bar_chart_showing_level = "Layer";
      } else if (selected_level == 1) {
        // component part
        raw_data = Data.component_grid /*[this.selected_slice]*/;
        compared_data = this.current_selected_regions.componentIDs;
        this.bar_chart_showing_level = "Component";
      } else if (selected_level == 2) {
        // cell part
        raw_data = Data.cell_grid /*[this.selected_slice]*/;
        compared_data = this.current_selected_regions.cellIDs;
        this.bar_chart_showing_level = "Cells";
      }
      compared_data.forEach((match) => {
        let arr_temp: number[] = [];
        let arr_OH: number[] = [];
        raw_data.forEach((layerID, i) => {
          if (layerID == match) {
            arr_temp.push(Data.vox_grid /*[this.selected_slice]*/[i]);
            arr_OH.push(Data.OH_grid /*[this.selected_slice]*/[i]);
          }
        });
        this.data_bar_chart.push({
          id: match,
          voxCount: arr_temp.length,
          meanTemp: Number(d3.mean(arr_temp) ? d3.mean(arr_temp) : 0),
          meanOH: Number(d3.mean(arr_OH) ? d3.mean(arr_OH) : 0),
          stdTemp: Number(d3.deviation(arr_temp) ? d3.deviation(arr_temp) : 0),
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
            this.size.height / 2 - this.margin.bottom + 35
          })`
        )
        .attr("dy", "0.5rem") // relative distance from the indicated coordinates.
        .style("text-anchor", "middle")
        .style("font-weight", "bold")
        .text(
          "Temperature/OH of Voxels in Level " + this.scatter_plot_showing_level
        ); // text content

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
        .range([this.margin.left, this.size.width - this.margin.right])
        .domain(xCategories)
        .padding(0.1); // spacing between the categories

      // In viewport (our screen), the topmost side always refer to 0 in the vertical coordinates in pixels (y).
      let yScale = d3
        .scaleLinear()
        .range([this.size.height / 2 - this.margin.bottom, this.margin.top]) //bottom side to the top side on the screen
        .domain([yMin < 0 ? yMin : 0, yMax]);

      const xAxis = chartContainer
        .append("g")
        .attr(
          "transform",
          `translate(0, ${this.size.height / 2 - this.margin.bottom})`
        )
      xAxis.call(d3.axisBottom(xScale));

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
        .text(this.bar_chart_showing_level + " Ids")
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

      //zooming functionality
      const zoom = d3
        .zoom()
        .scaleExtent([1, 3])
        //.translateExtent([[this.margin.left, 0],[this.size.width - this.margin.right, this.size.height]])
        .on("zoom", zoomed);

      chartContainer
        .call(zoom);

      const barchart = chartContainer
        .append("g");
      
      barchart
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
        .append("g");
      
      error_bars
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
            this.size.height / 2 - this.margin.bottom + 35
          })`
        )
        .attr("dy", "0.5rem") // relative distance from the indicated coordinates.
        .style("text-anchor", "middle")
        .style("font-weight", "bold")
        .text("Statistics from Level " + this.bar_chart_showing_level); // text content

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
      let marginLeft = this.margin.left;
      let sizeWidth = this.size.width;
      let marginRight = this.margin.right;
      let local_data_bar_chart = this.data_bar_chart;
      function zoomed({transform}) {
        // recover the new scale
        xScale.range([marginLeft, sizeWidth - marginRight].map(d => transform.applyX(d)));
        
        barchart
          .selectAll("rect")
          .attr("x", (d: BarChart) => xScale(String(d.id)) as number)
          .attr("width", xScale.bandwidth())
        
        // clear error bars
        error_bars
          .selectAll("path")
          .remove();

        // plot error bars again
        error_bars
          .selectAll("path")
          .data<BarChart>(local_data_bar_chart)
          .join("path")
          .attr("d", erro_bar)
          .style("fill", "none")
          .style("stroke", "#000000")
          .style("opacity", 1.0);
        
        xAxis.call(d3.axisBottom(xScale));
      }
    },
    plotChart() {
      d3.select("#bar-svg2").selectAll("*").remove(); // Clean all the elements in the chart
      this.scatterPlot();

      d3.select("#tooltip").remove();

      d3.select("#bar-svg3").selectAll("*").remove(); // Clean all the elements in the chart
      this.barChart();
    },
  },
  watch: {
    rerender(newSize) {
      if (!isEmpty(newSize)) {
        this.plotChart();
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

