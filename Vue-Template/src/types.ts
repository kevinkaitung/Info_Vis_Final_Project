// Global types and interfaces are stored here.
export interface Margin {
    readonly left: number;
    readonly right: number;
    readonly top: number;
    readonly bottom: number;
}

export interface ComponentSize {
    width: number;
    height: number;
}

export interface Point {
    readonly posX: number;
    readonly posY: number;
}

export interface Bar{
    readonly value: number;
}

export interface Pos{
    x: number;
    y: number;
    z: number;
}

export interface Range{
    max: number;
    min: number;
}

export interface ScatterPlot {
    temp: number;
    OH: number;
}

export interface SelectedRegions {
    layerIDs: number[];
    componentIDs: number[];
    cellIDs: number[];
}

export interface BarChart {
    id: number;
    voxCount: number;
    meanTemp: number;
    meanOH: number;
    stdTemp: number;
    stdOH: number;
}