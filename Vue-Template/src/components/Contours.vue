<script lang="ts">
import * as d3 from "d3";
import Data from '../../data/temp_data_s30.json'; /* Example of reading in data directly from file */
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

            grid_layer: [] as Number[],
            threshold_layer: [] as Number[],

            grid_cmpt: [] as Number[],
            threshold_cmpt: [] as Number[],

            grid_cell: [] as Number[],
            threshold_cell: [] as Number[],

            siteCmptIds: [] as Number[],


            filter_val: -1, 
            layer_selected: -1, cmpt_selected: -1, cell_selected: -1,
            clr: !(this.cmpt_selected) ? "orange" : "brown",
            lyr_val_to_ind: {11:0, 15:1},

            beep: 0

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
        this.grid_layer = Data.layer_grid
        this.threshold_layer = Data.layer_thresh;
        this.grid_cmpt = Data.component_grid;
        this.threshold_cmpt = Data.component_thresh;
        this.grid_cell = Data.cell_grid;
        this.threshold_cell = Data.cell_thresh;
        this.siteCmptIds = Data.siteCmptIds

        

    },
    methods: {

        shapeContains(inner_polygon, outer_polygon) {
            const geo = d3.geoPath()
            let bounds = geo.bounds(outer_polygon)
            let center = geo.centroid(inner_polygon)
            if ((bounds[0][0] <= center[0] && center[0] <= bounds[1][0]) && (bounds[0][1] <= center[1] && center[1] <= bounds[1][1])) {
                return true
            }
            else{
                return false
            }
        },

        transform: ({type, value, coordinates}) => {
            let count = 0
            return {type, value, coordinates: coordinates.map(rings => {
                return rings.map(points => {
                    return points.map(([x, y]) => ([x,200-y]));
                });
            })};
        },

        voxContourPolygons: (contours, grid_layer, grid_cmpt, shapeContains) => {
            let pNum = 0
            let contourPolygons = contours.map((layer, l_i) => {
                return layer.coordinates.map((polygon, polygon_i) => {
                    let cmpt_val = -1
                    pNum++
                    polygon[0].forEach(([x,y]) => {
                        let index = Math.round(x)+ (300 * Math.round(200-y))
                            cmpt_val = (grid_layer[index] == l_i + 1 && grid_cmpt[index] > cmpt_val) ? grid_cmpt[index] : cmpt_val
                    })
                    return {type: "Polygon", value: layer.value, coordinates: polygon, layer: l_i+1, cmpt: cmpt_val, polygonNum: pNum}
                })
            })

            contourPolygons[1].forEach((p2, i) => {
                for (let p1 of contourPolygons[0]){
                    if (shapeContains(p2,p1)) {
                        contourPolygons[1][i]["containedBy"] = p1.cmpt
                        break
                    }
                }
            })
            return contourPolygons
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
            .style("font-size", "0.5em")
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
            let vox_contours = d3.contours().size([300, 200]).thresholds(v.threshold_vox)(v.grid_vox).map(v.transform),
            cell_contours = v.generateContours(v.threshold_cell,v.grid_cell).slice(1).map((c) => c[1]),
            vox_contour_polygons = v.voxContourPolygons(vox_contours, this.grid_layer, this.grid_cmpt,v.shapeContains),
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

            const dynamic_contours = vox_contour_polygons.forEach((layer) => { 
                chartContainer.append("g")
                .attr("stroke", "black")
                .attr("stroke-thickness", "0.5px")
                .selectAll("path")
                .data(layer)
                .join("path")
                //.attr("visibility", d => { return d.polygonNum == 3 ?  "visible" : "hidden" })
                .attr("fill", d => v.color(d.value, v.filter_val,"orange"))
                .attr("opacity", 1)
                .attr("d", d3.geoPath())
                .attr("class", function (d){ 
                let cmptstr = d.cmpt > 0 ? "cmpt_" + d.cmpt : "cmpt_none"
                let containedby = "ccmpt_" + d.containedBy
                    return "contours layer_" + d.layer + " " + cmptstr + " " + containedby }
                )
                .attr("id", function (d){ return "p" + d.layer + "_" + d.polygonNum})
                .on('mouseover', function (event, d) {
                    if(v.layer_selected < 0){
                        d3.selectAll(".layer_" + d.layer).transition()
                        .duration('50')
                        .attr("fill", "yellow")
                        d3.select("#toptext").text("hovered: layer" + d.layer)} 
                    else if(v.cmpt_selected < 0 && d.value == v.filter_val){
                        d3.selectAll(".cmpt_" + d.cmpt).transition()
                        .duration('50')
                        .attr("fill", "yellow")
                        d3.select("#toptext").text("hovered: cmpt" + d.cmpt)
                    }
                })
                .on('click mouseout', function(event, d) { 
                    if(v.layer_selected < 0){
                        if (event.type == "click"){
                            v.filter_val = d.value
                            v.layer_selected = d.layer;
                            d3.selectAll(".contours").attr("visibility", "hidden")
                            d3.selectAll(".layer_" + d.layer)
                            .attr("visibility", "visible")
                            d3.selectAll(".layer_" + (d.layer+1))
                            .attr("visibility", "visible").attr("fill","white")
                            d3.select("#toptext2").text("last clicked: layer" + d.layer)
                        }
                        d3.selectAll(".contours").each(function (d){
                            d3.select(this)
                            .transition().duration('50')
                            .attr("fill", v.color(d.value,v.filter_val,"orange"))
                        })
                        
                        d3.select("#toptext").text("hovered: none")
                         //d3.selectAll("path.cmpt"+ v.lyr_val_to_ind[v.filter_val]).attr("visibility", "visible")
                    }
                    else if(v.cmpt_selected < 0 && d.value == v.filter_val){
                        if (event.type == "click"){
                            v.cmpt_selected = d.cmpt 
                            d3.select("#toptext2").text("last clicked: cmpt" + d.cmpt)
                            d3.selectAll(".contours").attr("visibility", "hidden")
                            d3.selectAll(".cells_" + d.cmpt).attr("visibility", "visible")
                            d3.selectAll(".cmpt_" + d.cmpt).attr("visibility", "visible").attr("fill", "brown")
                            d3.selectAll(".ccmpt_" + d.cmpt)
                            .attr("visibility", "visible").attr("fill","white")
                            //bounded_zoomIn(event, d, d.cmpt)
                        }
                        d3.selectAll(".cmpt_" + d.cmpt).transition()
                        .duration('50')
                        .attr("fill",  v.cmpt_selected > 0 ? "brown" : d => v.color(d.value, v.filter_val, "orange"))
                        
                    }
                    d3.select("#toptext").text("hovered: none")
                })
                    
            })

            let cells =  chartContainer.append("g").attr("visibility", "hidden")
                        .attr("fill","none")
                        .selectAll("path")
                        .data(cell_contours)
                        .join("path")
                        .attr("class", function (d){return "cells_" + v.siteCmptIds[d.value]})
                        .attr("id", function (d){ return "site_" + d.value })
                        .attr("fill", "orange")
                        .attr("fill-opacity", 1)
                        .attr("d", d3.geoPath())
                        .on('mouseover', function () {
                            d3.select(this).transition()
                            .duration('50')
                            .attr('fill', "yellow").attr("fill-opacity", 1)
                            d3.select("#toptext").text("hovered: " + this.id)
                        })
                        .on('click', function(event, d) {
                            let sval = d.value
                            d3.select(this).attr("class", "cells" + v.siteCmptIds[d.value] + "_clicked").attr("fill-opacity", 0.8)
                            d3.select("#toptext2").text("last clicked: " + this.id)
                        })
                        .on('mouseout', function () {
                            let sval = parseInt(this.id.substring(5))
                            d3.select(this).transition()
                            .duration('50')
                            .attr('fill', "orange").attr("fill-opacity", 1)
                            d3.selectAll(".cells" + v.siteCmptIds[sval] + "_clicked").transition()
                            .duration('50')
                            .attr("fill-opacity", 0.8)
                            d3.select("#toptext").text("hovered: none")
                        })
            

            
            chartContainer.append("g").call(this.xAxis);
            chartContainer.append("g") .call(this.yAxis);    
        },
        // level_selected = 0 (for layer), 1 (for component), 2 (for cell)
        passParamsToAuxiliary(level_selected, id_selected) {
            this.emitter.emit('selected_info_passed', {'level_selected': level_selected, 'id_selected': id_selected});
        },
    },
    watch: {
        rerender(newSize) { 
            if (!isEmpty(newSize)) {
                d3.select('#contour-svg').selectAll('*').remove() // Clean all the elements in the chart
                this.initChart();
            }
        },
        layer_selected(new_selected, old_selected) {
            this.passParamsToAuxiliary(0, new_selected);
        },
        cmpt_selected(new_selected, old_selected) {
            this.passParamsToAuxiliary(1, new_selected);
        },
        cell_selected(new_selected, old_selected) {
            this.passParamsToAuxiliary(2, new_selected);
        },
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

