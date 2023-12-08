<script lang="ts">
import * as d3 from "d3";
import Data from '../../data/temp_data_s30.json'; /* Default data is slice taken at x=30 */
import { isEmpty, debounce } from 'lodash';


export default {
    data() {
        // Here we define the local states of this component. If you think the component as a class, then these are like its private variables.
        return {

            slice: -1,

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
            layer_selected: -1, cmpt_selected: -1, cells_selected: [], cells_count: 0,
            clr: !(this.cmpt_selected) ? "orange" : "brown",
            lyr_val_to_ind: {11:0, 15:1},

        }
    },
   
    computed: {
        // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
        rerender() {
            return (!isEmpty(this.grid_vox)) && this.size
        },
    },

     // Anything in here will only be executed once.
    created() {
       
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
        this.slice = Data.slice
        
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
            let coords = coordinates.map(rings => {
                return rings.map(points => {
                    return points.map(([x, y]) => {
                        return [x,200-y]
                    });
                })
            })
            return {type, value, coordinates: coords}
        },

        voxContourPolygons: (contours, grid_layer, grid_cmpt, shapeContains) => {
            let pNum = 0, lyrVoxArr = [contours[0].layerVox-contours[1].layerVox, contours[1].layerVox, 0]
            let contourPolygons = contours.map((layer, l_i) => {
                return layer.coordinates.map((polygon, polygon_i) => {
                    let cmpt_val = -1
                    pNum++
                    polygon[0].forEach(([x,y]) => {
                        let index = Math.floor(x)+ (300 * Math.floor(200-y))
                            cmpt_val = (grid_layer[index] == l_i + 1 && grid_cmpt[index] > cmpt_val) ? grid_cmpt[index] : cmpt_val
                    })
                    return {type: "Polygon", value: layer.value, coordinates: polygon, layer: l_i+1, 
                    layerVox: lyrVoxArr[l_i], cmpt: cmpt_val, polygonNum: pNum}
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
        xAxis: (g) => {
            const x = d3.scaleLinear([0, 300], [0, 300]);
            g.attr("transform", `translate(0,${200})`)
            .style("font-size", "0.3em")
            .call(d3.axisTop(x).tickSizeInner([3]).ticks(300 / 200 * 10))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick").filter(d => x.domain().includes(d)).remove())
        },
        yAxis: (g) => {
            const y = d3.scaleLinear([0, 200], [200, 0]);
            g.attr("transform", "translate(-1,0)")
            .style("font-size", "0.3em")
            .call(d3.axisRight(y).tickSizeInner([3]))
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
            empty_contour = d3.contours().size([300, 200]).thresholds([0, v.threshold_vox[0]])(v.grid_vox).map(v.transform)[0],
            cell_contours = v.generateContours(v.threshold_cell,v.grid_cell).slice(1).map((c) => c[1]),
            vox_contour_polygons = v.voxContourPolygons(vox_contours, this.grid_layer, this.grid_cmpt,v.shapeContains),
            colors = vox_contour_polygons.map((lyr) => {
                if (lyr.length > 0) {
                    return d3.scaleSequential(d3.extent(v.threshold_vox), d3.interpolateRgb("orange", "white"))(lyr[0].value)
                }
                else return ''
            })

            let showTooltip = function (event, d) {
            if((v.layer_selected < 0 || d.layer == v.layer_selected) || (v.cmpt_selected > 0 && d.layer == undefined)){
                if (event.type == "mouseover"){
                tooltip.transition().duration(100).style("visibility","visible");
            }
            let lyrText = v.layer_selected > 0 ? "Layer " + v.layer_selected : "Layer " + d.layer,
            cmptText = v.layer_selected > 0 ? 
                v.cmpt_selected > 0? "<br>Component " + v.cmpt_selected : "<br>Component " + d.cmpt 
                : "",
            cellText =  v.cmpt_selected > 0 ? "<br>Cell " + d.value  : "",
            elemText = lyrText + cmptText + cellText,
            pos = d3.pointer(event),
            y_offset = v.cmpt_selected > 0 ? 15 : 0
            tooltip
            .html(
            elemText+
              "<br>y: " + Math.floor(pos[0]) + ", z: " +  Math.floor(pos[1])
            )
            .style("left", event.x - tooltip.property("offsetWidth") + "px")
            .style("top", event.y - tooltip.property("offsetHeight") - y_offset + "px");
            }
            else{
                tooltip.transition().duration(100).style("visibility","hidden");
            }
            
            };

            let hideTooltip = function (event, d) {
            tooltip.transition().duration(100).style("visibility","hidden");
            };

            function zoomed(e) { 
                chartContainer.attr("transform", e.transform); 
            } 
            const zoom = d3.zoom().translateExtent([[0,0],[300,200]]).scaleExtent([1, 3]).on("zoom", zoomed)
            .filter(function (event) {
                return event.type != "dblclick";
            });

            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let chartContainer = d3.select('#contour-svg')
            .attr("viewBox", [0, 0, 300, 200])
            .style("border","1px solid black")
            .call(zoom).append("g")

            const empty_space = chartContainer.append("g").
            selectAll("path")
            .data([empty_contour])
            .join("path")
            .attr("d", d3.geoPath())
            .attr("fill", "white")
            .on('dblclick', function(e,d) {
                if(v.cmpt_selected > 0 && v.layer_selected > 0){
                    d3.selectAll(".cells_" + v.cmpt_selected).attr("class", "cells_" + v.cmpt_selected).attr("fill", colors[v.layer_selected-1])
                    .attr("fill-opacity", 1)
                    cells.attr("visibility", "hidden")
                    v.cmpt_selected = -1
                    d3.selectAll(".layer_" + v.layer_selected).attr("visibility", "visible").attr("fill", colors[v.layer_selected-1])
                    d3.selectAll(".layer_" + (v.layer_selected+1)).attr("visibility", "visible").attr("fill","white")
                    v.cells_selected = []
                    v.cells_count = v.cells_selected.length
                }
                else if (v.layer_selected > 0) {
                    d3.selectAll(".contours").attr("visibility", "visible")
                    if(v.layer_selected != v.threshold_layer.slice(-1)){
                       let val = vox_contour_polygons[v.layer_selected][0].value
                       d3.selectAll(".layer_" + (v.layer_selected + 1)).attr("fill", colors[v.layer_selected])
                    }
                    v.filter_val = -1
                    v.layer_selected = -1
                }
            })


            const dynamic_contours = vox_contour_polygons.forEach((layer) => { 
                chartContainer.append("g")
                .attr("stroke", "black")
                .attr("stroke-thickness", "0.5px")
                .selectAll("path")
                .data(layer)
                .join("path")
                .attr("fill", d => colors[d.layer-1])
                .attr("opacity", 1)
                .attr("d", d3.geoPath())
                .attr("class", function (d){ 
                let cmptstr = d.cmpt > 0 ? "cmpt_" + d.cmpt : "cmpt_none"
                let containedby = "ccmpt_" + d.containedBy
                    return "contours layer_" + d.layer + " " + cmptstr + " " + containedby }
                )
                .attr("id", function (d){ return "p" + d.layer + "_" + d.polygonNum})
                .on('mouseover', function (event, d) {
                    showTooltip(event, d)
                    if(v.layer_selected < 0){
                        v.passHoverID(d.layer, true)
                        d3.selectAll(".layer_" + d.layer).transition()
                        .duration('50')
                        .attr("fill", "yellow")
                        d3.select("#toptext").text("hovered: layer" + d.layer)} 
                    else if(v.cmpt_selected < 0 && d.value == v.filter_val){
                        v.passHoverID(d.cmpt, true)
                        d3.selectAll(".cmpt_" + d.cmpt).transition()
                        .duration('50')
                        .attr("fill", "yellow")
                        d3.select("#toptext").text("hovered: cmpt" + d.cmpt)
                    }
                })
                .on("mousemove", showTooltip)
                .on('click mouseout', function(event, d) { 
                    hideTooltip(event, d)
                    if(v.layer_selected < 0){
                        if (event.type == "click"){
                            v.filter_val = d.value
                            v.layer_selected = d.layer;
                            d3.selectAll(".contours").attr("visibility", "hidden")
                            d3.selectAll(".layer_" + d.layer)
                            .attr("visibility", "visible").attr("fill", colors[d.layer-1])
                            if(v.layer_selected != v.threshold_layer.slice(-1)){
                                d3.selectAll(".layer_" + (d.layer+1))
                                .attr("visibility", "visible").attr("fill","white")
                                d3.select("#toptext2").text("last clicked: layer" + d.layer)
                            }
                        }
                        else{
                            v.passHoverID(d.layer, false)
                            d3.selectAll(".contours").each(function (d){
                            d3.select(this)
                            .transition().duration('50')
                            .attr("fill", colors[d.layer-1])
                            })
                        }
                        d3.select("#toptext").text("hovered: none")
                    }
                    else if(v.cmpt_selected < 0 && d.value == v.filter_val){
                        if (event.type == "click"){
                            v.cmpt_selected = d.cmpt 
                            d3.select("#toptext2").text("last clicked: cmpt" + d.cmpt)
                            d3.selectAll(".contours").attr("visibility", "hidden")
                            d3.selectAll(".cells_" + d.cmpt).attr("visibility", "visible").attr("fill", colors[d.layer-1])
                            d3.selectAll(".cmpt_" + d.cmpt).attr("visibility", "visible").attr("fill", "brown")
                            d3.selectAll(".ccmpt_" + d.cmpt)
                            .attr("visibility", "visible").attr("fill","white")
                            //bounded_zoomIn(event, d, d.cmpt)
                        }
                        v.passHoverID(d.cmpt, false)
                        d3.selectAll(".cmpt_" + d.cmpt).transition()
                        .duration('50')
                        .attr("fill",  v.cmpt_selected > 0 ? "brown" : d => colors[d.layer-1])
                        
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
                        .attr("opacity", 1)
                        .attr("fill", v.layer_selected > 0 ? colors[v.layer_selected-1] : "orange")
                        .attr("d", d3.geoPath())
                        .on('mouseover', function (event, d) {
                            v.passHoverID(d.value, true)
                            showTooltip(event, d)
                            d3.select(this).transition()
                            .duration('50')
                            .attr('fill', "yellow").attr("opacity", 1)
                            d3.select("#toptext").text("hovered: " + this.id)
                        })
                        .on("mousemove", showTooltip)
                        .on('click', function(event, d) {
                            if(!v.cells_selected.includes(d.value)){
                                v.cells_selected.push(d.value)
                                v.cells_count = v.cells_selected.length
                                d3.select(this).attr('opacity', 0.9)
                            }
                            d3.select("#toptext2").text("last clicked: " + this.id)
                        })
                        .on('mouseout', function (event, d) {
                            v.passHoverID(d.value, false)
                            hideTooltip(event, d)
                            let selection =  d3.select(this).transition()
                                .duration('50')
                                
                            if(!v.cells_selected.includes(d.value)){
                                selection.attr("opacity", 1).attr('fill', colors[v.layer_selected-1])
                            }
                            else{
                                selection.attr('fill', "yellow").attr('opacity', 0.9)
                            }
                            d3.select("#toptext").text("hovered: none")
                        })
        

            chartContainer.append("g").call(this.xAxis);
            chartContainer.append("g") .call(this.yAxis);
            
            let tooltip = d3.select("#root")
            .append("div")
            .attr("id", "iv_tooltip")
            .style("visibility", "hidden")
            .attr("class", "tooltip")
            .style("background-color", "black")
            .style("color", "white")
            .style("border-radius", "5px")
            .style("padding", "10px")
            .style("font-size", "10px")
            .style("position", "absolute");


            },

        // level_selected = 0 (for layer), 1 (for component), 2 (for cell)
        passParamsToAuxiliary(level_selected, id_selected) {
            this.emitter.emit('selected_info_passed', {'level_selected': level_selected, 'id_selected': id_selected});
        },
        passHoverID(id_hovered, is_hover_in) {
            this.emitter.emit('hovered_info_passed', {'id_hovered': id_hovered, 'is_hover_in': is_hover_in});
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
        cells_count(new_selected, old_selected) {
            this.passParamsToAuxiliary(2, this.cells_selected);
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
<template>
    <div  style="font-size:30px;"><b>Turbulent Combustion Visualization</b></div>
    <div class="chart-container">
        <div style="font-size:20px;"><b>z</b></div>
        <div ref="contourContainer"> 
            <svg id="contour-svg" width="100%" height="66%">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
            </svg>
        </div>
        <div style="text-align:right;font-size:20px;" ><b>y</b></div>
        <div style="font-size:25px;"><b>x</b> = {{this.slice}}</div>
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>

