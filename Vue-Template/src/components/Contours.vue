<script lang="ts">
import * as d3 from "d3";
import Data from '../../data/temp_data_s45.json'; /* Example of reading in data directly from file */
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { Bar, ComponentSize, Margin } from '../types';

// A "extends" B means A inherits the properties and methods from B.
interface CategoricalBar extends Bar{
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
            margin: {left: 40, right: 20, top: 20, bottom: 60} as Margin, 

            grid_vox: [] as Number[],
            threshold_vox: [] as Number[],

            grid_cmpt: [] as Number[][],
            threshold_cmpt: [] as Number[][],

            grid_cell: [] as Number[][],
            threshold_cell: [] as Number[][],

            grid_layer: [] as Number[],
            threshold_layer: [] as Number[],

            filter_val: -1, 
            layer_selected: false, cmpt_selected: false, cell_selected: false,
            clr: !(this.cmpt_selected) ? "orange" : "brown",
            lyr_val_to_ind: { 11:0, 15:1  }

        }
    },
   
    computed: {
        // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
        rerender() {
            return (!isEmpty(this.bars)) && this.size
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
       
        if (isEmpty(Data)) return;
        this.grid_vox = Data.vox_grid;
        this.threshold_vox = Data.vox_thresh;
        this.grid_cmpt = Data.component_grid;
        this.threshold_cmpt = Data.component_thresh;
        this.grid_cell = Data.cell_grid;
        this.threshold_cell = Data.cell_thresh;

    },
    methods: {
        transform: ({type, value, coordinates}) => {
            let count = 0
            return {type, value, coordinates: coordinates.map(rings => {
                return rings.map(points => {
                    return points.map(([x, y]) => ([x,200-y]));
                });
            })};
        },
        generateContours(thresh, grid_in) {
            let contours = thresh.map((c) => { 
                if(c > 0){
                    let grid = grid_in.map((g) => g == c ? c : -1), threshold_c = [0,c];
                    return d3.contours().smooth(true).size([300, 200]).thresholds(threshold_c)(grid).map(this.transform);
                }
            })
            return contours;   
        },
        color(val, filter_val, base_color) {
            if (filter_val == -1) return d3.scaleSequential(d3.extent(this.threshold_vox), d3.interpolateRgb(base_color, "white"))(val)
            else if (val == filter_val) return base_color
            else return "white"
        },
        stroke(val, filter_val){
            if (filter_val == -1) return 0.5
            else if (filter_val == 11) return 0.5
            else if (filter_val == 15 && filter_val == val) return 0.5
            else return 0
        },
        xAxis: (g) => {
            const x = d3.scaleLinear([0, 300], [0, 300]);
            g.attr("transform", `translate(0,${200})`)
            .call(d3.axisTop(x).ticks(300 / 200 * 10))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick").filter(d => x.domain().includes(d)).remove())
        },
        yAxis: (g) => {
            const y = d3.scaleLinear([0, 200], [200, 0]);
            g.attr("transform", "translate(-1,0)")
            .style("font-size", "0.5em")
            .call(d3.axisRight(y))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick").filter(d => y.domain().includes(d)).remove())
        },
        onResize() {  // record the updated size of the target element
            let target = this.$refs.contourContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {

            let v = this;
            let contour = d3.contours().size([300, 200]).thresholds(this.threshold_vox)(this.grid_vox).map(this.transform),
            lyr_val_to_ind = {11:0, 15:1} 

            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let chartContainer = d3.select('#contour-svg').attr("viewBox", [0, 0, 300, 200]).style("border","1px solid black")

            chartContainer.append("text")
            .text("hovered: none")
            .attr("id", "toptext").attr("x", 2)
            .attr("y", 5)
            .attr("font-size", 6)

            chartContainer.append("text")
            .text("last clicked: none")
            .attr("id", "toptext2").attr("x", 2)
            .attr("y", 13)
            .attr("font-size", 6)

            const vox_dynamic = chartContainer.append("g")
            .attr("stroke",  "black")
            .attr("stroke-thickness", 0.5)
            .style("border", "1px solid black")
            .selectAll("path")
            .data(contour)
            .join("path")
            .attr("class", "layer_d")
            .attr("id", function (d){return "layer_" + d.value})
            .attr("visibility", g => {return !this.layer_selected ? "visible" : "hidden"})
            .attr("stroke-opacity", d => this.stroke(d.value, this.filter_val))
            .attr("fill", d => this.color(d.value, this.filter_val, "orange"))
            .attr("d", d3.geoPath())
            .on('mouseover', function (event, d) {
                if(!v.layer_selected){
                    d3.select(this).transition().duration('50')
                    .attr("fill", "yellow")
                    d3.select("#toptext").text("hovered: " + this.id)
                } 
            })
            .on('click mouseout', function(event) { 
                if(!v.layer_selected){
                    if (event.type == "click"){
                        v.filter_val = event.type == "click" ? parseInt(this.id.substring(6)) : v.filter_val;
                        v.layer_selected = event.type == "click" ? true : v.layer_selected;
                        d3.select("#toptext2").text("last clicked: " + this.id)
                    }
                    d3.selectAll(".layer_d").each(function (){
                        d3.select(this)
                        .transition().duration('50')
                        .attr("stroke-opacity", v.stroke(this.id.substring(6), v.filter_val))
                        .attr("fill", v.color(this.id.substring(6),v.filter_val,v.clr))
                    })
                    d3.selectAll("path.cmpt"+ v.lyr_val_to_ind[v.filter_val]).attr("visibility", "visible")
                    d3.select("#toptext").text("hovered: none")
                }
            })

            v.threshold_cmpt.forEach((t,i) => {
                let contour_data = v.generateContours(t,v.grid_cmpt[i]).slice(1).map((c) => c[1])

                chartContainer.append("g")
                .attr("fill","none")
                .attr("visibility", "hidden")
                .selectAll("path")
                .data(contour_data)
                .join("path")
                .attr("class", "cmpt"+i)
                .attr("id", function(d){ return "cmpt_" + d.value })
                .attr("d", d3.geoPath())
                .attr("fill", "yellow")
                .attr("opacity", 0)
                .on('mouseover', function () {
                    d3.select(this).transition()
                    .duration('50')
                    .attr('opacity', 1)
                    d3.select("#toptext").text("hovered: " + this.id)})
                .on('click', function(event) {if (!v.cmpt_selected){
                    v.cmpt_selected = event.type == "click" ? true : v.cmpt_selected;
                    d3.selectAll(".layer_d").each(function (){
                        d3.select(this)
                        .attr("stroke-opacity", v.stroke(this.id.substring(6), v.filter_val))
                        .attr("fill", v.color(this.id.substring(6), v.filter_val, "brown"))
                    })
                    d3.selectAll("path.cmpt"+v.lyr_val_to_ind[v.filter_val]).attr("visibility", "hidden")
                    d3.selectAll("path.cell"+v.lyr_val_to_ind[v.filter_val]).attr("visibility", "visible")
                    d3.select("#toptext2").text("last clicked: " + this.id)
                }})
                .on('mouseout', function () {
                    d3.selectAll(".cmpt"+v.lyr_val_to_ind[v.filter_val]).transition()
                    .duration('50')
                    .attr('opacity', 0)
                    d3.select("#toptext").text("hovered: none")})
            })

            v.threshold_cell.forEach((t,i) => {
                let contour_data = v.generateContours(t,v.grid_cell[i]).slice(1).map((c) => c[1])
    
                chartContainer.append("g").attr("visibility", "hidden")
                .attr("fill","none")
                .selectAll("path")
                .data(contour_data)
                .join("path")
                .attr("class", "cell"+i)
                .attr("id", function (d){ return "site_" + d.value })
                .attr("fill", "orange")
                .attr("fill-opacity", 1)
                .attr("d", d3.geoPath())
                .on('mouseover', function () {
                    d3.select(this).transition()
                    .duration('50')
                    .attr('fill', "yellow").attr("fill-opacity", 1)
                    d3.select("#toptext").text("currently selected: " + this.id)})
                .on('click', function() {
                    d3.select(this).attr("class", "cell" + i + "_clicked").attr("fill-opacity", 0.8)
                    d3.select("#toptext2").text("last clicked: " + this.id)
                })
                .on('mouseout', function () {
                    d3.select(this).transition()
                    .duration('50')
                    .attr('fill', "orange").attr("fill-opacity", 1)
                    d3.selectAll(".cell" + i + "_clicked").transition()
                    .duration('50')
                    .attr("fill-opacity", 0.8)
                    d3.select("#toptext").text("hovered: none")
                })
            })
            
            chartContainer.append("g").call(this.xAxis);
            chartContainer.append("g") .call(this.yAxis);    
        }
    },
    watch: {
        rerender(newSize) { 
            if (!isEmpty(newSize)) {
                d3.select('#contour-svg').selectAll('*').remove() // Clean all the elements in the chart
                this.initChart();
            }
        }
    },
    // The following are general setup for resize events.
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100)) ;
        this.onResize();
        this.initChart();

    },
    beforeDestroy() {
       window.removeEventListener('resize', this.onResize)
    }
}

</script>

<!-- "ref" registers a reference to the HTML element so that we can access it via the reference in Vue.  -->
<!-- We use flex (d-flex) to arrange the layout-->
<template>
    <div class="chart-container d-flex" ref="contourContainer">
        <svg id="contour-svg" width="900px" height="600px">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
        </svg>
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>

