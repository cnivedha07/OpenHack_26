export interface Hospital {
  id: string;
  name: string;
  status: "Active" | "Suspicious" | "Excluded" | "Training";
  trust_score: number;
  privacy_status: string;
  validation_status: string;
  sample_count: number;
  train_size?: number;
  val_size?: number;
  accuracy: number;
  loss: number;
  train_accuracy?: number;
  val_accuracy?: number;
  generalization_gap?: number;
  fit_status?: "Overfit" | "Underfit" | "Well-fit" | "Compromised" | "Not Trained Yet";
  attack_active: boolean;
  active_attack: string;
}

export interface FeatureFusionStats {
  cnn_usage_pct: number;
  ann_usage_pct: number;
  bert_usage_pct: number;
  fusion_mechanism: string;
}

export interface DashboardSummary {
  current_round: number;
  total_rounds: number;
  global_accuracy: number;
  global_loss: number;
  global_trust?: number;
  is_training_active?: boolean;
  is_paused?: boolean;
  dp_enabled?: boolean;
  flagged_count?: number;
  attacks_live?: number;
  hospitals: Hospital[];
  feature_fusion_stats: FeatureFusionStats;
  federated_round_history: any[];
  model_version: string;
}
