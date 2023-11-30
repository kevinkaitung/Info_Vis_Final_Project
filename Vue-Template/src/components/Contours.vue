<script lang="ts">
import * as d3 from "d3";
import Data from '../../data/temp_slice_data.json'; /* Example of reading in data directly from file */
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

            grid_cell: [] as Number[],
            threshold_cell: [] as Number[],

            grid_layer: [] as Number[],
            threshold_layer: [] as Number[],

            filter_val: -1, 
            layer_selected: false, cmpt_selected: false, cell_selected: false,
            clr: !(this.cmpt_selected) ? "orange" : "brown" 

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
            const x = d3.scaleLinear([0, 300], [0, 300 + 28]);
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
            contours_cmpt_1 = this.generateContours(this.threshold_cmpt[0],this.grid_cmpt[0]).slice(1).map((c) => c[1]),
            contours_cells = this.generateContours(this.threshold_cell,this.grid_cell).slice(1).map((c) => c[1]);

            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let chartContainer = d3.select('#contour-svg').attr("viewBox", [0, 0, 300 + 28, 200])
            .style("display", "block").style("margin", "0 -14px").style("width", "calc(100% + 28px)");

            chartContainer.append("text")
            .text("hello!")
            .attr("id", "toptext").attr("x", 10)
            .attr("y", 4)
            .attr("font-size", 7)

            chartContainer.append("text")
            .text("hiya!")
            .attr("id", "toptext2").attr("x", 10)
            .attr("y", 12)
            .attr("font-size", 7)

            const vox_dynamic = chartContainer.append("g")
            .attr("stroke",  "black")
            .attr("stroke-thickness", 0.5)
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
                    d3.select("#toptext").text("currently selected: " + this.id)
                } 
            })
            .on('click mouseout', function(event) { 
                if(!v.layer_selected){
                    v.filter_val = event.type == "click" ? parseInt(event.target.id.substring(6)) : v.filter_val;
                    d3.selectAll(".layer_d").each(function (){
                        d3.select(this)
                        .transition().duration('50')
                        .attr("stroke-opacity", v.stroke(this.id.substring(6), v.filter_val))
                        .attr("fill", v.color(this.id.substring(6),v.filter_val,v.clr))
                    })
                    components_1.attr("visibility", g => {return v.filter_val == 11 ? "visible" : "hidden"})
                    //components_2.attr("visibility", g => {return filter_val == 15 ? "visible" : "hidden"})
                    d3.select("#toptext").text("currently selected: none")
                    v.layer_selected = event.type == "click" ? true : v.layer_selected;
                    if(event.type == "click") d3.select("#toptext2").text("last selected: " + this.id)
                }
            })
            .on('dblclick', function(event, g) { 
                if(v.layer_selected && !v.cmpt_selected){
                    v.filter_val = event.type == "dblclick" ? -1 : v.filter_val;
                    v.layer_selected = event.type == "dblclick" ? false : v.layer_selected;
                    components_1.attr("visibility", "hidden")
                    vox_dynamic.transition().duration('50').attr("visibility", "visible").attr("stroke-opacity", 0.5);
                    d3.selectAll(".layer_d").each(function (){
                        d3.select(this)
                        .transition().duration('50')
                        .attr("stroke-opacity", v.stroke(this.id.substring(6), v.filter_val))
                        .attr("fill", v.color(this.id.substring(6),v.filter_val,"orange"))
                    })
                }
            })

            const components_1 = chartContainer.append("g")
            .attr("fill","none")
            .attr("visibility", "hidden")
            .selectAll("path")
            .data(contours_cmpt_1)
            .join("path")
            .attr("class", "cmpt1")
            .attr("id", function(d){ return "cmpt_" + d.value })
            .attr("d", d3.geoPath())
            .attr("fill", "yellow")
            .attr("fill", "yellow")
            .attr("opacity", 0)
            .on('mouseover', function (d, i) {
                d3.select(this).transition().duration('50')
                .attr('opacity', 0.7)
                d3.select("#toptext").text("currently selected: " + this.id)})
            .on('click', function(event) {
                if (!v.cmpt_selected){
                    d3.selectAll(".layer_d").each(function (){
                        d3.select(this)
                        .transition().duration('50')
                        .attr("stroke-opacity", v.stroke(this.id.substring(6), v.filter_val))
                        .attr("fill", v.color(this.id.substring(6),v.filter_val,"brown"))
                    })
                    components_1.attr("visibility", "hidden")
                    //components_2.attr("visibility","hidden")
                    cells.attr("visibility", "visible")
                    v.cmpt_selected = event.type == "click" ? true : v.cmpt_selected;
                    d3.select("#toptext2").text("last selected: " + this.id)
                    
             }})
            .on('mouseout', function (d, i) {
                d3.selectAll(".cmpt1").transition().duration('50')
                .attr('opacity', 0)
                d3.select("#toptext").text("currently selected: none")
            })
            .on('dblclick', function(event, g) { 
                v.filter_val = event.type == "dblclick" ? -1 : v.filter_val;
                v.layer_selected = event.type == "dblclick" ? false : v.layer_selected;
                components_1.attr("visibility", "hidden")
                vox_dynamic.attr("visibility", "visible").attr("stroke-opacity", 0.5)
                d3.selectAll(".layer_d").each(function (){
                        d3.select(this)
                        .transition().duration('50')
                        .attr("stroke-opacity", v.stroke(this.id.substring(6), v.filter_val))
                        .attr("fill", v.color(this.id.substring(6),v.filter_val,"orange"))
                })
            });

            const cells = chartContainer.append("g").attr("visibility", "hidden")
            .selectAll("path")
            .data(contours_cells)
            .join("path")
            .attr("class", "cell1")
            .attr("id", function (d){ return "site_" + d.value })
            .attr("fill", "orange")
            .attr("fill-opacity", 1)
            .attr("d", d3.geoPath())
            .on('mouseover', function (d, i) {
                d3.select(this).transition().duration('50')
               .attr('fill', "yellow").attr("fill-opacity", 1)
                d3.select("#toptext").text("currently selected: " + this.id)
            })
            .on('click', function(event, d) {
                d3.select(this).attr("class", "cell1_clicked").attr("fill-opacity", 0.8)
                d3.select("#toptext2").text("last selected: " + this.id)
            })
            .on('mouseout', function (d, i) {
                d3.selectAll(".cell1").transition().duration('50')
               .attr('fill', "orange").attr("fill-opacity", 1)
                d3.selectAll(".cell1_clicked").transition().duration('50')
               .attr("fill-opacity", 0.8)
                d3.select("#toptext").text("currently selected: none")
    
            })
            chartContainer.append("g").call(this.xAxis);
            chartContainer.append("g") .call(this.yAxis);    
        }
    },
    watch: {
        rerender(newSize) { 
            console.log("hi")
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
        <svg id="contour-svg" width="100%" height="100%">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
        </svg>
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>

