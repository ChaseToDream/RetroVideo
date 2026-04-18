import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 300000,
})

export async function uploadVideo(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/videos/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    },
  })
  return res.data
}

export async function getVideo(videoId) {
  const res = await api.get(`/videos/${videoId}`)
  return res.data
}

export async function getPreview(videoId, preset) {
  const res = await api.get(`/videos/${videoId}/preview`, {
    params: { preset },
    responseType: 'blob',
  })
  return URL.createObjectURL(res.data)
}

export async function processVideo(videoId, preset, params) {
  const res = await api.post(`/videos/${videoId}/process`, { preset, params })
  return res.data
}

export async function getTask(taskId) {
  const res = await api.get(`/tasks/${taskId}`)
  return res.data
}

export async function getTaskProgress(taskId) {
  const res = await api.get(`/tasks/${taskId}/progress`)
  return res.data
}

export async function listPresets() {
  const res = await api.get('/presets')
  return res.data
}

export async function getPreset(name) {
  const res = await api.get(`/presets/${name}`)
  return res.data
}

export function getDownloadUrl(taskId) {
  return `/api/v1/downloads/${taskId}`
}

export async function deleteVideo(videoId) {
  const res = await api.delete(`/videos/${videoId}`)
  return res.data
}
