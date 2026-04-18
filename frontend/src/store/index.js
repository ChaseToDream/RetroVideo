import { create } from 'zustand'

const useStore = create((set, get) => ({
  video: null,
  uploadProgress: 0,
  isUploading: false,
  selectedPreset: 'nokia_6600',
  presetDetail: null,
  customParams: {},
  previewUrl: null,
  isPreviewLoading: false,
  task: null,
  taskProgress: null,

  setVideo: (video) => set({ video }),
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  setIsUploading: (loading) => set({ isUploading: loading }),
  setSelectedPreset: (preset) => set({ selectedPreset: preset, customParams: {} }),
  setPresetDetail: (detail) => set({ presetDetail: detail }),
  setCustomParams: (params) => set({ customParams: params }),
  setPreviewUrl: (url) => set({ previewUrl: url }),
  setIsPreviewLoading: (loading) => set({ isPreviewLoading: loading }),
  setTask: (task) => set({ task }),
  setTaskProgress: (progress) => set({ taskProgress: progress }),

  reset: () => set({
    video: null,
    uploadProgress: 0,
    isUploading: false,
    selectedPreset: 'nokia_6600',
    presetDetail: null,
    customParams: {},
    previewUrl: null,
    isPreviewLoading: false,
    task: null,
    taskProgress: null,
  }),
}))

export default useStore
