# Turbulent Combustion Visualization

This Vue application visualizes slices of 3D turbulent combustion data taken along the x-axis. 

## Libraries/Dependencies Installed in this Framework
 * D3.js v7 for visualization
 * [axios](https://axios-http.com/docs/intro) for API.
 * [pinia](https://pinia.vuejs.org/introduction.html) for store management in Vue.js
 * [Vuetify](https://next.vuetifyjs.com/en/components/all/) for UI that follows Google Material Design 3.
 * [lodash](https://lodash.com/) for utility functions in JavaScript.

## Set-up

To set up the application: 

1. Install packages from package.json:
`cd ./Vue-Template`, then `npm install`

2. Run the application with `npm run dev`, which will be hosted at `localhost:3000`

Currently, the application can only display one slice at a given time. 
By default, it will load in the data from and generate visualizations for the slice at `x = 30`.
However, multiple slice files are available to visualize within the `data` folder. 

To change the slice to visualize, change the line `import data from '../../data/temp_data_s30.json'` in both `/src/Contours.Vue` and `/src/Auxillary.Vue` to be `import data from '../../data/temp_data_sN.json'` where N is the number of an available slice in the `data` folder. 

## Navigation/Interaction:

Upon loading the application, the interactive view will display all the geometric elements for the given slice while the scatterplot will display all the voxel data for that slice. Meanwhile, the barchart will display the aggregate OH statistics for each of the contour layers. 


Overview/Layer View: Hover over contour shapes to highlight layers; Click on a layer to filter out unselected layers.
Component View: Hover over component to highlight it; (For layer 1 components) Click on component to show cells for that component;
Cell View: Hover over cell to highlight; Click to select;


# Vite 

**NOTE: the following is from Vite, which you can ignore it.**

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

## Type Support For `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin) to make the TypeScript language service aware of `.vue` types.

If the standalone TypeScript plugin doesn't feel fast enough to you, Volar has also implemented a [Take Over Mode](https://github.com/johnsoncodehk/volar/discussions/471#discussioncomment-1361669) that is more performant. You can enable it by the following steps:

1. Disable the built-in TypeScript Extension
   1. Run `Extensions: Show Built-in Extensions` from VSCode's command palette
   2. Find `TypeScript and JavaScript Language Features`, right click and select `Disable (Workspace)`
2. Reload the VSCode window by running `Developer: Reload Window` from the command palette.
