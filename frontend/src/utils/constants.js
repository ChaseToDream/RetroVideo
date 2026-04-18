export const PRESET_LIST = [
  { name: 'nokia_3310', label: 'Nokia 3310', device: '诺基亚 3310' },
  { name: 'nokia_6600', label: 'Nokia 6600', device: '诺基亚 6600' },
  { name: 'moto_razr_v3', label: 'Moto RAZR V3', device: '摩托罗拉 RAZR V3' },
  { name: 'sony_k750i', label: 'Sony K750i', device: '索爱 K750i' },
  { name: 'nokia_n73', label: 'Nokia N73', device: '诺基亚 N73' },
]

export const RESOLUTION_OPTIONS = [
  { label: '128×96 (SQCIF)', width: 128, height: 96 },
  { label: '176×144 (QCIF)', width: 176, height: 144 },
  { label: '320×240 (QVGA)', width: 320, height: 240 },
  { label: '352×288 (CIF)', width: 352, height: 288 },
]

export const FPS_OPTIONS = [8, 10, 12, 15, 24]
export const BITRATE_OPTIONS = ['32k', '48k', '64k', '96k', '128k', '192k']

export const COLOR_OPTIONS = [
  { label: '原色', value: 'original' },
  { label: '低饱和度', value: 'low_saturation' },
  { label: '偏黄', value: 'yellowish' },
  { label: '偏绿', value: 'greenish' },
  { label: '偏蓝', value: 'bluish' },
  { label: '高对比度', value: 'high_contrast' },
]

export const NOISE_OPTIONS = [
  { label: '无', value: 'none' },
  { label: '轻微', value: 'light' },
  { label: '中等', value: 'medium' },
  { label: '强烈', value: 'strong' },
]

export const AUDIO_OPTIONS = [
  { label: '原始', value: 'original' },
  { label: '低采样率 (8kHz)', value: 'low_sample' },
  { label: '单声道', value: 'mono' },
  { label: '低采样率+单声道', value: 'low_mono' },
  { label: '静音', value: 'mute' },
]

export const OUTPUT_FORMAT_OPTIONS = [
  { label: '3GP', value: '3gp' },
  { label: 'MP4', value: 'mp4' },
]
