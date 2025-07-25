from lukefi.metsi.domain.pre_ops import *
from lukefi.metsi.domain.sim_ops import *
from lukefi.metsi.sim.generators import *

default = {} # Empty dict declares a default output content

csv_and_json = {
    'csv': default,
    'json': default
}

control_structure = {
    "app_configuration": {
        "state_format": "xml",  # options: fdm, vmi12, vmi13, xml, gpkg
        # "state_input_container": "csv",  # Only relevant with fdm state_format. Options: pickle, json
        # "state_output_container": "csv",  # options: pickle, json, csv, null
        # "derived_data_output_container": "pickle",  # options: pickle, json, null
        "formation_strategy": "partial",
        "evaluation_strategy": "depth",
        "run_modes": ["preprocess", "export_prepro", "simulate", "postprocess", "export"]
    },
    "preprocessing_operations": [
        #scale_area_weight,
        generate_reference_trees,  # reference trees from strata, replaces existing reference trees
        # preproc_filter
        # "supplement_missing_tree_heights",
        # "supplement_missing_tree_ages",
        # "generate_sapling_trees_from_sapling_strata"
    ],
    "preprocessing_params": {
        generate_reference_trees: [
            {
                "n_trees": 10,
                "method": "weibull",
                "debug": False
            }
        ],
        preproc_filter: [
            {
                "remove trees": "sapling or stems_per_ha == 0",
                "remove stands": "site_type_category == 0",  # not reference_trees
                "remove stands": "site_type_category == None"
            }
        ]
    },
    "simulation_events": [
        {
            "time_points": [0],
            "generators": [
                {sequence: [planting]}
            ]
        },
        {
            "time_points": [0, 5, 10, 15, 20, 25],
            "generators": [
                {sequence: [
                    cross_cut_standing_trees,
                    collect_standing_tree_properties,
                    calculate_npv,
                    calculate_biomass,
                    report_state
                ]}
            ]
        },
        {
            "time_points": [2, 7, 17],
            "generators": [
                {
                    alternatives: [
                        do_nothing,
                        thinning_from_below,
                        thinning_from_above,
                        first_thinning,
                        even_thinning,
                        {
                            sequence: [
                                clearcutting,
                                planting
                                # operations for renewal after clearcutting go here
                            ]
                        }
                    ]
                },
                {
                    sequence: [
                        cross_cut_felled_trees,
                        collect_felled_tree_properties
                    ]
                }
            ]
        },
        {
            "time_points": [5, 10, 15, 20, 25],
            "generators": [
                {sequence: [report_period]}
            ]
        },
        {
            "time_points": [25],
            "generators": [
                {sequence: [report_collectives]}
            ]
        },
        {
            "time_points": [0, 5, 10, 15, 20, 25],
            "generators": [
                {sequence: [grow_acta]}
                # "grow_motti"
            ]
        }
    ],
    "operation_params": {
        first_thinning: [
            {
                "thinning_factor": 0.97,
                "e": 0.2,
                "dominant_height_lower_bound": 11,
                "dominant_height_upper_bound": 16
            }
        ],
        thinning_from_below: [
            {
                "thinning_factor": 0.97,
                "e": 0.2
            }
        ],
        thinning_from_above: [
            {
                "thinning_factor": 0.98,
                "e": 0.2
            }
        ],
        even_thinning: [
            {
                "thinning_factor": 0.9,
                "e": 0.2
            }
        ],
        calculate_biomass: [
            {"model_set": 1}
        ],
        report_collectives: [
            {
                "identifier": "identifier",
                "area": "area",
                "npv_1_percent": "net_present_value.value[(net_present_value.interest_rate==1) & "
                "(net_present_value.time_point == 25)]",
                "npv_2_percent": "net_present_value.value[(net_present_value.interest_rate==2) & "
                "(net_present_value.time_point == 25)]",
                "npv_3_percent": "net_present_value.value[(net_present_value.interest_rate==3) & "
                "(net_present_value.time_point == 25)]",
                "npv_4_percent": "net_present_value.value[(net_present_value.interest_rate==4) & "
                "(net_present_value.time_point == 25)]",
                "npv_5_percent": "net_present_value.value[(net_present_value.interest_rate==5) & "
                "(net_present_value.time_point == 25)]",

                # Stock volumes at state years
                "stock_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 0)]",
                "stock_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 5)]",
                "stock_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 10)]",
                "stock_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 20)]",

                # Harves volumes at event years
                "harvest_2": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 2)]",
                "harvest_7": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 7)]",
                "harvest_17": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 17)]",

                # HARVEST VALUES ADAPTING harvest volumes in period (by end year)
                "harvest_value_2": "cross_cutting.value_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 2)]",
                "harvest_value_7": "cross_cutting.value_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 7)]",
                "harvest_value_17": "cross_cutting.value_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 17)]",

                # EVENTS * HARVEST VALUES ADAPTING harvest volumes in period (by end year)
                "harvest_value_first_2": "cross_cutting.value_per_ha[(cross_cutting.operation=='first_thinning') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 2)]",
                "harvest_value_below_2": "cross_cutting.value_per_ha[(cross_cutting.operation=='thinning_from_below') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 2)]",
                "harvest_value_above_2": "cross_cutting.value_per_ha[(cross_cutting.operation=='thinning_from_above') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 2)]",
                "harvest_value_even_2": "cross_cutting.value_per_ha[(cross_cutting.operation=='even_thinning') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 2)]",
                "harvest_value_clearcut_2": "cross_cutting.value_per_ha[(cross_cutting.operation=='clearcutting') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 2)]",

                "harvest_value_first_7": "cross_cutting.value_per_ha[(cross_cutting.operation=='first_thinning') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 7)]",
                "harvest_value_below_7": "cross_cutting.value_per_ha[(cross_cutting.operation=='thinning_from_below') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 7)]",
                "harvest_value_above_7": "cross_cutting.value_per_ha[(cross_cutting.operation=='thinning_from_above') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 7)]",
                "harvest_value_even_7": "cross_cutting.value_per_ha[(cross_cutting.operation=='even_thinning') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 7)]",
                "harvest_value_clearcut_7": "cross_cutting.value_per_ha[(cross_cutting.operation=='clearcutting') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 7)]",

                "harvest_value_first_17": "cross_cutting.value_per_ha[(cross_cutting.operation=='first_thinning') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 17)]",
                "harvest_value_below_17": "cross_cutting.value_per_ha[(cross_cutting.operation=='thinning_from_below') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 17)]",
                "harvest_value_above_17": "cross_cutting.value_per_ha[(cross_cutting.operation=='thinning_from_above') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 17)]",
                "harvest_value_even_17": "cross_cutting.value_per_ha[(cross_cutting.operation=='even_thinning') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 17)]",
                "harvest_value_clearcut_17": "cross_cutting.value_per_ha[(cross_cutting.operation=='clearcutting') & "
                "(cross_cutting.source == 'harvested') & (cross_cutting.time_point == 17)]",

                # stock volumes at state years per species (1 = pine, 2 = spruce, ..., 38 = unknown)
                # this is done to get the volumes of each tree species to compute the CO2 more accurately
                # ages of the different species are read according to these same enumerations

                "stock_1_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 1)]",
                "stock_1_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 1)]",
                "stock_1_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 1)]",
                "stock_1_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 1)]",

                "stock_2_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 2)]",
                "stock_2_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 2)]",
                "stock_2_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 2)]",
                "stock_2_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 2)]",

                "stock_3_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 3)]",
                "stock_3_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 3)]",
                "stock_3_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 3)]",
                "stock_3_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 3)]",

                "stock_4_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 4)]",
                "stock_4_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 4)]",
                "stock_4_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 4)]",
                "stock_4_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 4)]",

                "stock_5_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 5)]",
                "stock_5_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 5)]",
                "stock_5_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 5)]",
                "stock_5_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 5)]",

                "stock_6_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 6)]",
                "stock_6_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 6)]",
                "stock_6_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 6)]",
                "stock_6_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 6)]",

                "stock_7_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 7)]",
                "stock_7_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 7)]",
                "stock_7_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 7)]",
                "stock_7_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 7)]",

                "stock_8_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 8)]",
                "stock_8_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 8)]",
                "stock_8_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 8)]",
                "stock_8_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 8)]",

                "stock_9_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 9)]",
                "stock_9_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 9)]",
                "stock_9_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 9)]",
                "stock_9_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 9)]",

                "stock_10_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 10)]",
                "stock_10_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 10)]",
                "stock_10_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 10)]",
                "stock_10_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 10)]",

                "stock_11_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 11)]",
                "stock_11_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 11)]",
                "stock_11_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 11)]",
                "stock_11_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 11)]",

                "stock_12_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 12)]",
                "stock_12_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 12)]",
                "stock_12_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 12)]",
                "stock_12_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 12)]",

                "stock_13_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 13)]",
                "stock_13_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 13)]",
                "stock_13_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 13)]",
                "stock_13_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 13)]",

                "stock_14_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 14)]",
                "stock_14_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 14)]",
                "stock_14_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 14)]",
                "stock_14_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 14)]",

                "stock_15_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 15)]",
                "stock_15_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 15)]",
                "stock_15_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 15)]",
                "stock_15_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 15)]",

                "stock_16_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 16)]",
                "stock_16_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 16)]",
                "stock_16_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 16)]",
                "stock_16_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 16)]",

                "stock_17_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 17)]",
                "stock_17_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 17)]",
                "stock_17_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 17)]",
                "stock_17_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 17)]",

                "stock_18_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 18)]",
                "stock_18_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 18)]",
                "stock_18_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 18)]",
                "stock_18_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 18)]",

                "stock_19_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 19)]",
                "stock_19_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 19)]",
                "stock_19_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 19)]",
                "stock_19_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 19)]",

                "stock_20_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 20)]",
                "stock_20_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 20)]",
                "stock_20_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 20)]",
                "stock_20_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 20)]",

                "stock_21_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 21)]",
                "stock_21_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 21)]",
                "stock_21_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 21)]",
                "stock_21_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 21)]",

                "stock_22_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 22)]",
                "stock_22_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 22)]",
                "stock_22_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 22)]",
                "stock_22_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 22)]",

                "stock_23_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 23)]",
                "stock_23_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 23)]",
                "stock_23_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 23)]",
                "stock_23_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 23)]",

                "stock_24_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 24)]",
                "stock_24_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 24)]",
                "stock_24_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 24)]",
                "stock_24_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 24)]",

                "stock_25_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 25)]",
                "stock_25_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 25)]",
                "stock_25_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 25)]",
                "stock_25_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 25)]",

                "stock_26_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 26)]",
                "stock_26_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 26)]",
                "stock_26_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 26)]",
                "stock_26_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 26)]",

                "stock_27_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 27)]",
                "stock_27_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 27)]",
                "stock_27_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 27)]",
                "stock_27_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 27)]",

                "stock_28_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 28)]",
                "stock_28_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 28)]",
                "stock_28_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 28)]",
                "stock_28_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 28)]",

                "stock_29_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 29)]",
                "stock_29_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 29)]",
                "stock_29_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 29)]",
                "stock_29_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 29)]",

                "stock_30_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 30)]",
                "stock_30_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 30)]",
                "stock_30_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 30)]",
                "stock_30_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 30)]",

                "stock_31_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 31)]",
                "stock_31_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 31)]",
                "stock_31_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 31)]",
                "stock_31_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 31)]",

                "stock_32_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 32)]",
                "stock_32_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 32)]",
                "stock_32_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 32)]",
                "stock_32_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 32)]",

                "stock_33_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 33)]",
                "stock_33_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 33)]",
                "stock_33_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 33)]",
                "stock_33_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 33)]",

                "stock_34_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 34)]",
                "stock_34_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 34)]",
                "stock_34_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 34)]",
                "stock_34_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 34)]",

                "stock_35_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 35)]",
                "stock_35_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 35)]",
                "stock_35_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 35)]",
                "stock_35_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 35)]",

                "stock_36_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 36)]",
                "stock_36_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 36)]",
                "stock_36_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 36)]",
                "stock_36_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 36)]",

                "stock_37_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 37)]",
                "stock_37_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 37)]",
                "stock_37_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 37)]",
                "stock_37_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 37)]",

                "stock_38_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 0) & (cross_cutting.species == 38)]",
                "stock_38_5": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 5) & (cross_cutting.species == 38)]",
                "stock_38_10": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 10) & (cross_cutting.species == 38)]",
                "stock_38_20": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & (cross_cutting.time_point == 20) & (cross_cutting.species == 38)]",
            }
        ],
        report_period: [
            {"overall_volume": "cross_cutting.volume_per_ha"}
        ],
        calculate_npv: [
            {"interest_rates": [1, 2, 3, 4, 5]}
        ],
        collect_standing_tree_properties: [
            {"properties": ["stems_per_ha", "species", "breast_height_diameter", "height",
                            "breast_height_age", "biological_age", "saw_log_volume_reduction_factor"]}
        ],
        collect_felled_tree_properties: [
            {"properties": ["stems_per_ha", "species", "breast_height_diameter", "height"]}
        ],
        planting: [
            {"tree_count": 10}
        ]
    },
    "operation_file_params": {
        thinning_from_above: {
            "thinning_limits": "data/parameter_files/Thin.txt"
        },
        cross_cut_felled_trees: {
            "timber_price_table": "data/parameter_files/timber_price_table.csv"
        },
        cross_cut_standing_trees: {
            "timber_price_table": "data/parameter_files/timber_price_table.csv"
        },
        clearcutting: {
            "clearcutting_limits_ages": "data/parameter_files/renewal_ages_southernFI.txt",
            "clearcutting_limits_diameters": "data/parameter_files/renewal_diameters_southernFI.txt"
        },
        planting: {
            "planting_instructions": "data/parameter_files/planting_instructions.txt"
        },
        calculate_npv: {
            "land_values": "data/parameter_files/land_values_per_site_type_and_interest_rate.json",
            "renewal_costs": "data/parameter_files/renewal_operation_pricing.csv"
        }
    },
    "run_constraints": {
        first_thinning: {
            "minimum_time_interval": 50
        },
        clearcutting: {
            "minimum_time_interval": 50
        }
    },
    "post_processing": {
        "operation_params": {
            do_nothing: [
                {"param": "value"}
            ]
        },
        "post_processing": [
            do_nothing
        ]
    },
    "export": [
        {
            "format": "J",
            "cvariables": [
                "identifier", "year", "site_type_category", "land_use_category", "soil_peatland_category"
            ],
            "xvariables": [
                "identifier",
                "area",
                "npv_1_percent", 
                "npv_2_percent", 
                "npv_3_percent", 
                "npv_4_percent", 
                "npv_5_percent",
                # stock volumes at state years
                "stock_0",
                "stock_5",
                "stock_10",
                "stock_20",
                # harvest volumes at event years
                "harvest_2",
                "harvest_7",
                "harvest_17",
                # harvest VALUES ADAPTING volumes in period (by end year)
                "harvest_value_2",
                "harvest_value_7",
                "harvest_value_17",
                "harvest_value_first_2",
                "harvest_value_below_2",
                "harvest_value_above_2",
                "harvest_value_even_2",
                "harvest_value_clearcut_2",
                "harvest_value_first_7",
                "harvest_value_below_7",
                "harvest_value_above_7",
                "harvest_value_even_7",
                "harvest_value_clearcut_7",
                "harvest_value_first_17",
                "harvest_value_below_17",
                "harvest_value_above_17",
                "harvest_value_even_17",
                "harvest_value_clearcut_17",
                # stock volumes
                "stock_1_0",
                "stock_1_5",
                "stock_1_10",
                "stock_1_20",
                "stock_2_0",
                "stock_2_5",
                "stock_2_10",
                "stock_2_20",
                "stock_3_0",
                "stock_3_5",
                "stock_3_10",
                "stock_3_20",
                "stock_4_0",
                "stock_4_5",
                "stock_4_10",
                "stock_4_20",
                "stock_5_0",
                "stock_5_5",
                "stock_5_10",
                "stock_5_20",
                "stock_6_0",
                "stock_6_5",
                "stock_6_10",
                "stock_6_20",
                "stock_7_0",
                "stock_7_5",
                "stock_7_10",
                "stock_7_20",
                "stock_8_0",
                "stock_8_5",
                "stock_8_10",
                "stock_8_20",
                "stock_9_0",
                "stock_9_5",
                "stock_9_10",
                "stock_9_20",
                "stock_10_0",
                "stock_10_5",
                "stock_10_10",
                "stock_10_20",
                "stock_11_0",
                "stock_11_5",
                "stock_11_10",
                "stock_11_20",
                "stock_12_0",
                "stock_12_5",
                "stock_12_10",
                "stock_12_20",
                "stock_13_0",
                "stock_13_5",
                "stock_13_10",
                "stock_13_20",
                "stock_14_0",
                "stock_14_5",
                "stock_14_10",
                "stock_14_20",
                "stock_15_0",
                "stock_15_5",
                "stock_15_10",
                "stock_15_20",
                "stock_16_0",
                "stock_16_5",
                "stock_16_10",
                "stock_16_20",
                "stock_17_0",
                "stock_17_5",
                "stock_17_10",
                "stock_17_20",
                "stock_18_0",
                "stock_18_5",
                "stock_18_10",
                "stock_18_20",
                "stock_19_0",
                "stock_19_5",
                "stock_19_10",
                "stock_19_20",
                "stock_20_0",
                "stock_20_5",
                "stock_20_10",
                "stock_20_20",
                "stock_21_0",
                "stock_21_5",
                "stock_21_10",
                "stock_21_20",
                "stock_22_0",
                "stock_22_5",
                "stock_22_10",
                "stock_22_20",
                "stock_23_0",
                "stock_23_5",
                "stock_23_10",
                "stock_23_20",
                "stock_24_0",
                "stock_24_5",
                "stock_24_10",
                "stock_24_20",
                "stock_25_0",
                "stock_25_5",
                "stock_25_10",
                "stock_25_20",
                "stock_26_0",
                "stock_26_5",
                "stock_26_10",
                "stock_26_20",
                "stock_27_0",
                "stock_27_5",
                "stock_27_10",
                "stock_27_20",
                "stock_28_0",
                "stock_28_5",
                "stock_28_10",
                "stock_28_20",
                "stock_29_0",
                "stock_29_5",
                "stock_29_10",
                "stock_29_20",
                "stock_30_0",
                "stock_30_5",
                "stock_30_10",
                "stock_30_20",
                "stock_31_0",
                "stock_31_5",
                "stock_31_10",
                "stock_31_20",
                "stock_32_0",
                "stock_32_5",
                "stock_32_10",
                "stock_32_20",
                "stock_33_0",
                "stock_33_5",
                "stock_33_10",
                "stock_33_20",
                "stock_34_0",
                "stock_34_5",
                "stock_34_10",
                "stock_34_20",
                "stock_35_0",
                "stock_35_5",
                "stock_35_10",
                "stock_35_20",
                "stock_36_0",
                "stock_36_5",
                "stock_36_10",
                "stock_36_20",
                "stock_37_0",
                "stock_37_5",
                "stock_37_10",
                "stock_37_20",
                "stock_38_0",
                "stock_38_5",
                "stock_38_10",
                "stock_38_20"
            ]
        },
        {
            "format": "rm_schedules_events_timber",
            "filename": "timber_sums.txt"
        },
        {
            "format": "rm_schedules_events_trees",
            "filename": "trees.txt"
        }
    ]
}

# The preprocessing export format is added as an external module
control_structure['export_prepro'] = csv_and_json

__all__ = ['control_structure']
