const path = require('path');
var webpack = require("webpack");
// const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = (env, argv) => {
   // Get the dataset from environment variables
   // const dataset = env && env.DATASET
   // if (!dataset) {
   //    throw new Error("Please provide the dataset filename in the environment variable DATASET")
   // }

   // const datasets = Array.from({ length: 20 }, (_, i) => `llava1.5_with_image_q20_i10_s0/${String(i).padStart(3, '0')}.json`);

   // return datasets.map(dataset => ({
   const baseConfig = {
      entry: './src/main.ts',
      devtool: 'inline-source-map',
      module: {
         rules: [
            {
               test: /\.tsx?$/,
               use: 'ts-loader',
               exclude: /node_modules/
            }
         ]
      },
      resolve: {
         extensions: ['.tsx', '.ts', '.js']
      },
      output: {
         filename: 'web.js',
         path: path.resolve(__dirname, 'web')
         // path: path.resolve(__dirname, `web/${path.basename(dataset, '.json')}`)  // Output to separate folders
      },
      devServer: {
         static: {
            directory: path.resolve(__dirname, 'web'),
         },
         compress: true,
         port: 8000,
      },
      plugins: [
         new webpack.DefinePlugin({
            _DEVMODE: !!(argv.mode == 'development')
            // _DATASET: JSON.stringify(dataset)  // Inject dataset filename
         }),
         // // Copy index.html, style.css, and baked_queues into each build folder
         // new CopyWebpackPlugin({
         //    patterns: [
         //        { from: 'web/index.html', to: '' },  // Copy index.html
         //        { from: 'web/style.css', to: '' },   // Copy CSS
         //        { from: 'web/baked_queues', to: 'baked_queues' },  // Copy datasets
         //        { from: 'web/img', to: 'img' } // Copy images
         //    ]
         // })
      ],
      // ignore file size warning
      performance: {
         hints: false,
      },
   };

   const productConfig = {
      ...baseConfig,
      entry: './src/main_prod_metric.ts',
      output: {
         filename: 'web_prod_metric.js',
         path: path.resolve(__dirname, 'web/prod_metric'),
      }
   };

   const vfMetricConfig = {
      ...baseConfig,
      entry: './src/main_vf_metric_only.ts',
      output: {
         filename: 'web_vf_metric_only.js',
         path: path.resolve(__dirname, 'web/vf_metric_only'),
      }
   }

   const contrastiveMetricConfig = {
      ...baseConfig,
      entry: './src/main_contrastive_metric_only.ts',
      output: {
         filename: 'web_contrastive_metric_only.js',
         path: path.resolve(__dirname, 'web/contrastive_metric_only'),
      }
   }

   // Return an array of configurations
   return [baseConfig, productConfig, vfMetricConfig, contrastiveMetricConfig];
};