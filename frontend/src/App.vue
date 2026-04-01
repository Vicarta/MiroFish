<template>
  <router-view />
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue'

const exactTextMap = {
  '模拟实例初始化': 'Simulation Instance Initialization',
  '初始化': 'Initializing',
  '新建simulation实例，拉取模拟World参数模版': 'Create a new simulation instance and load the world parameter template.',
  '异步任务Done': 'Async task done',
  '生成 Agent 人设': 'Generate Agent Personas',
  '结合上下文，自动调用工具从知识Graph梳理实体与Edges，初始化模拟个体，并基于Seed Materials赋予他们独特的行为与记忆': 'Use the graph and seed materials to initialize simulated people with distinct behavior patterns and memory.',
  'CurrentAgent数': 'Current agents',
  '预期Agent总数': 'Expected agents',
  'Seed MaterialsCurrent关联话题数': 'Linked seed topics',
  '已生成的 Agent 人设': 'Generated Agent Personas',
  '暂NoneBio': 'No bio yet',
  '生成双平台模拟配置': 'Generate Dual-Platform Simulation Config',
  'LLM 根据Simulation Requirement与Seed Materials，智能设置World时间流速、推荐算法、每个个体的活跃时间段、发言频率、事件触发等参数': 'Use the simulation requirement and seed materials to configure time flow, ranking logic, activity windows, posting cadence, and trigger events.',
  '模拟时长': 'Simulation duration',
  '总轮次': 'Total rounds',
  '每小时活跃': 'Agents per hour',
  '高峰时段': 'Peak hours',
  '工作时段': 'Work hours',
  '早间时段': 'Morning hours',
  '低谷时段': 'Off-peak hours',
  'Agent 配置': 'Agent Config',
  '活跃时段': 'Active hours',
  '发帖/时': 'Posts/hour',
  '评论/时': 'Comments/hour',
  '响应延迟': 'Response delay',
  '活跃度': 'Activity level',
  '情感倾向': 'Sentiment bias',
  '影响力': 'Influence',
  'Generating Final Report': 'Generate Final Report',
  'InsightForge 深度归因': 'InsightForge Deep Attribution',
  '对齐现实World种子数据与Simulation environment状态，结合Global/Local Memory机制，提供跨时空的深度归因分析': 'Align real-world source material with the simulation state and use global/local memory to produce deep attribution analysis.',
  'PanoramaSearch 全景追踪': 'PanoramaSearch Global Trace',
  '基于图结构的广度遍历算法，重构事件传播路径，捕获全量信息流动的拓扑结构': 'Traverse the graph to reconstruct propagation paths and capture the topology of information flow.',
  'QuickSearch 快速检索': 'QuickSearch Fast Retrieval',
  '基于 GraphRAG 的即时查询接口，优化索引效率，用于快速提取具体的Nodes属性与离散Facts': 'Use the GraphRAG query layer to quickly extract node attributes and discrete facts.',
  'InterviewSubAgent 虚拟访谈': 'InterviewSubAgent Virtual Interviews',
  '自主式访谈，能够并行与模拟World中个体进行多轮对话，采集非结构化的观点数据与心理状态': 'Run multi-round parallel interviews with simulated participants to gather unstructured opinions and mental-state signals.',
  'Bio': 'Bio',
  '进入Deep Interaction': 'Enter Deep Interaction',
  'Build Workflow': 'Build Workflow',
  'API Notes': 'API Notes',
  'Generation Progress': 'Generation Progress',
  'Build Complete': 'Build Complete',
  'Waiting for Report Agent...': 'Waiting for Report Agent...',
  'Chat with Report Agent': 'Chat with Report Agent',
  'Chat with any individual in the world': 'Chat with any individual in the world',
  'Select conversation target': 'Select conversation target',
  'Unknown role': 'Unknown role',
  'Send a survey into the world': 'Send a survey into the world',
}

const fragmentMap = [
  ['正在生成', 'Generating '],
  ['小时', 'hours'],
  [' 轮', ' rounds'],
  ['轮', 'rounds'],
  [' 个', ''],
  ['个', ''],
  ['全景追踪', 'Global Trace'],
  ['快速检索', 'Fast Retrieval'],
  ['虚拟访谈', 'Virtual Interviews'],
  ['深度归因', 'Deep Attribution'],
  ['Seed MaterialsCurrent', 'Seed-material'],
  ['World', 'world'],
]

const translatableAttributes = ['title', 'placeholder', 'aria-label']

const translateText = (value) => {
  if (!value) return value

  const trimmed = value.trim()
  if (!trimmed) return value

  let translated = exactTextMap[trimmed] || value

  for (const [from, to] of fragmentMap) {
    if (translated.includes(from)) {
      translated = translated.replaceAll(from, to)
    }
  }

  return translated
}

const translateNodeTree = (root) => {
  if (!root) return

  const textWalker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT)
  let textNode = textWalker.nextNode()

  while (textNode) {
    const nextNode = textWalker.nextNode()
    const translated = translateText(textNode.nodeValue)
    if (translated !== textNode.nodeValue) {
      textNode.nodeValue = translated
    }
    textNode = nextNode
  }

  const elementWalker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT)
  let element = elementWalker.currentNode

  while (element) {
    for (const attr of translatableAttributes) {
      if (element.hasAttribute?.(attr)) {
        const current = element.getAttribute(attr)
        const translated = translateText(current)
        if (translated !== current) {
          element.setAttribute(attr, translated)
        }
      }
    }
    element = elementWalker.nextNode()
  }
}

let observer = null
let rafId = null

const scheduleTranslation = () => {
  if (rafId) cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    translateNodeTree(document.body)
    document.documentElement.lang = 'en'
    document.title = translateText(document.title)
  })
}

onMounted(() => {
  scheduleTranslation()

  observer = new MutationObserver(() => {
    scheduleTranslation()
  })

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: translatableAttributes,
  })
})

onBeforeUnmount(() => {
  if (observer) observer.disconnect()
  if (rafId) cancelAnimationFrame(rafId)
})
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #000000;
}

::-webkit-scrollbar-thumb:hover {
  background: #333333;
}

/* 全局按钮样式 */
button {
  font-family: inherit;
}
</style>
