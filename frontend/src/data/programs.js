export const programs = [
  {
    id: 'focus-timer',
    name: '专注计时器',
    summary: '一个轻量的番茄钟工具，支持自定义时长与阶段提醒。',
    stack: ['Vue 3', 'Tailwind CSS'],
    status: '进行中',
    repoUrl: '',
    demoUrl: '',
  },
  {
    id: 'daily-notes',
    name: '每日随记',
    summary: '简洁的日记记录应用，强调快速输入和回顾体验。',
    stack: ['Flask', 'SQLite'],
    status: '维护中',
    repoUrl: '',
    demoUrl: '',
  },
  {
    id: 'image-cleanup',
    name: '图片整理助手',
    summary: '用于批量重命名与归档图片素材的小工具。',
    stack: ['Python'],
    status: '规划中',
    repoUrl: '',
    demoUrl: '',
  },
]

export function findProgramById(id) {
  return programs.find((item) => item.id === id)
}
