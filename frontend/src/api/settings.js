import service from './index'

export const getSettings = () => {
  return service({
    url: '/api/settings',
    method: 'get'
  })
}

export const updateSettings = (data) => {
  return service({
    url: '/api/settings',
    method: 'put',
    data
  })
}
