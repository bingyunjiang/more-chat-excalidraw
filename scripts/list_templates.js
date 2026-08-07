#!/usr/bin/env node
/**
 * 模板列表与预览脚本
 * 
 * 用法：
 *   node scripts/list_templates.js                      # 列出所有模板
 *   node scripts/list_templates.js --json               # JSON 格式输出
 *   node scripts/list_templates.js --preview flowchart  # 预览模板 SVG
 *   node scripts/list_templates.js --preview --all      # 预览所有模板
 */

const path = require('path');
const fs = require('fs');

const TEMPLATES = {
  flowchart: {
    name: '流程图 Flowchart',
    description: '纵向或横向：矩形步骤 + 菱形决策 + 箭头',
    layout: 'vertical',
    complexity: 'all',
    elements: ['ellipse', 'rectangle', 'diamond', 'arrow', 'text'],
    scenes: ['business-process', 'workflow', 'step-by-step'],
    colors: { primary: '#a5d8ff', decision: '#fff3bf', end: '#b2f2bb' }
  },
  architecture: {
    name: '架构图 Architecture',
    description: '分层：用户层 → 应用层 → 服务层 → 数据层',
    layout: 'layered',
    complexity: 'medium',
    elements: ['frame', 'rectangle', 'ellipse', 'arrow', 'text'],
    scenes: ['tech-arch', 'system-design', 'deployment'],
    colors: { user: '#dbe4ff', app: '#e5dbff', data: '#d3f9d8' }
  },
  sequence: {
    name: '时序图 Sequence',
    description: '三条竖线（角色）+ 横向箭头消息，编号 1/2/3',
    layout: 'horizontal',
    complexity: 'all',
    elements: ['rectangle', 'line', 'arrow', 'text'],
    scenes: ['communication', 'api-call', 'interaction'],
    colors: { actor1: '#a5d8ff', actor2: '#d0bfff', actor3: '#c3fae8' }
  },
  mindmap: {
    name: '思维导图 Mind Map',
    description: '中心主题 + 一级/二级分支',
    layout: 'tree',
    complexity: 'all',
    elements: ['ellipse', 'rectangle', 'line', 'arrow', 'text'],
    scenes: ['brainstorm', 'knowledge', 'idea'],
    colors: { center: '#a5d8ff', level1: '#d0bfff', level2: '#ffffff' }
  },
  swimlane: {
    name: '泳道图 Swimlane',
    description: '水平泳道按角色分区，流程穿越泳道',
    layout: 'swimlane',
    complexity: 'medium',
    elements: ['frame', 'rectangle', 'arrow', 'text'],
    scenes: ['business-process', 'role-responsibility', 'cross-team'],
    colors: { lane1: '#dbe4ff', lane2: '#e5dbff', lane3: '#d3f9d8' }
  },
  erd: {
    name: 'ER 图 ERD',
    description: '实体矩形 + 关系菱形/连线 + 基数标注',
    layout: 'free',
    complexity: 'all',
    elements: ['rectangle', 'diamond', 'line', 'arrow', 'text'],
    scenes: ['database-design', 'data-model', 'schema'],
    colors: { entity: '#a5d8ff', relation: '#fff3bf', attr: '#ffffff' }
  },
  hierarchy: {
    name: '层级图 Hierarchy',
    description: '自上而下树形结构，节点逐级展开',
    layout: 'tree',
    complexity: 'all',
    elements: ['rectangle', 'line', 'arrow', 'text'],
    scenes: ['org-chart', 'decomposition', 'taxonomy'],
    colors: { root: '#a5d8ff', level1: '#d0bfff', level2: '#b2f2bb' }
  },
  relationship: {
    name: '关系图 Relationship',
    description: '节点 + 连线 + 关系标注，无严格方向',
    layout: 'free',
    complexity: 'medium',
    elements: ['ellipse', 'rectangle', 'line', 'arrow', 'text'],
    scenes: ['dependency', 'network', 'influence'],
    colors: { primary: '#a5d8ff', secondary: '#d0bfff', line: '#868e96' }
  },
  comparison: {
    name: '对比图 Comparison',
    description: '左右两栏或表格，标明比较维度',
    layout: 'table',
    complexity: 'simple',
    elements: ['rectangle', 'line', 'text'],
    scenes: ['comparison', 'evaluation', 'pros-cons'],
    colors: { header: '#a5d8ff', colA: '#d0bfff', colB: '#c3fae8' }
  },
  timeline: {
    name: '时间线图 Timeline',
    description: '水平时间轴 + 关键节点 + 事件标注',
    layout: 'horizontal',
    complexity: 'all',
    elements: ['line', 'ellipse', 'text'],
    scenes: ['project-timeline', 'history', 'evolution'],
    colors: { axis: '#1e1e1e', node1: '#a5d8ff', node2: '#d0bfff', node3: '#b2f2bb', node4: '#ffd8a8' }
  }
};

const THEMES = {
  default: { name: '默认', roughness: 1, strokeWidth: 2, strokeColor: '#1e1e1e' },
  sketch: { name: '手绘', roughness: 2, strokeWidth: 3, strokeColor: '#2b2b2b' },
  blueprint: { name: '蓝图', roughness: 0, strokeWidth: 1, strokeColor: '#e8f4ff', bg: '#1e3a5f' },
  minimal: { name: '极简', roughness: 0, strokeWidth: 1, strokeColor: '#000000' }
};

function listTemplates(format) {
  if (format === 'json') {
    console.log(JSON.stringify({ templates: TEMPLATES, themes: THEMES }, null, 2));
    return;
  }
  console.log('='.repeat(70));
  console.log('Excalidraw 模板列表');
  console.log('='.repeat(70));
  for (const [key, tmpl] of Object.entries(TEMPLATES)) {
    console.log(`\n  [${key.padEnd(15)}] ${tmpl.name}`);
    console.log(`  ${''.padEnd(15)}  ${tmpl.description}`);
    console.log(`  ${''.padEnd(15)}  布局: ${tmpl.layout.padEnd(10)} 复杂度: ${tmpl.complexity.padEnd(10)} 元素: ${tmpl.elements.join(', ')}`);
  }
  console.log('\n' + '='.repeat(70));
  console.log('可用主题:');
  for (const [key, theme] of Object.entries(THEMES)) {
    console.log(`  [${key.padEnd(12)}] ${theme.name}`);
  }
  console.log('='.repeat(70));
}

function previewTemplate(name) {
  if (name === '--all') {
    for (const key of Object.keys(TEMPLATES)) {
      previewTemplate(key);
    }
    return;
  }
  const tmpl = TEMPLATES[name];
  if (!tmpl) {
    console.error(`未找到模板: ${name}`);
    console.error(`可用模板: ${Object.keys(TEMPLATES).join(', ')}`);
    process.exit(1);
  }
  console.log(`\n  ${tmpl.name}`);
  console.log(`  ${'-'.repeat(40)}`);
  console.log(`  描述: ${tmpl.description}`);
  console.log(`  布局: ${tmpl.layout}`);
  console.log(`  复杂度: ${tmpl.complexity}`);
  console.log(`  使用元素: ${tmpl.elements.join(', ')}`);
  console.log(`  适用场景: ${tmpl.scenes.join(', ')}`);
  console.log(`  色板: ${JSON.stringify(tmpl.colors)}`);
  console.log(`  参考文件: references/diagram-templates.md (第 ${getTemplateSection(name)} 节)`);
  console.log();
}

function getTemplateSection(name) {
  const sections = {
    flowchart: 1, architecture: 2, sequence: 3, mindmap: 4,
    swimlane: 5, erd: 6, hierarchy: 7, relationship: 8,
    comparison: 9, timeline: 10
  };
  return sections[name] || '?';
}

const args = process.argv.slice(2);
const format = args.includes('--json') ? 'json' : 'text';

if (args.includes('--preview')) {
  const idx = args.indexOf('--preview');
  const target = idx + 1 < args.length && !args[idx + 1].startsWith('--') ? args[idx + 1] : null;
  previewTemplate(target || '--all');
} else {
  listTemplates(format);
}
