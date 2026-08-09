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

const CJK_FONT_FAMILY = 'Ma Shan Zheng';
const CJK_FONT_FALLBACKS = [
  'Long Cang', 'Liu Jian Mao Cao', 'Hannotate SC',
  'HanziPen SC', 'Wawati SC', 'Kaiti SC', 'PingFang SC',
];
const hasCjk = (value) => /[\u2E80-\u9FFF\uF900-\uFAFF]/u.test(String(value));

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

const svgRenderer = (() => {
  try {
    return require('./lib/svg_render.js');
  } catch (e) {
    return null;
  }
})();

/**
 * Build a tiny representative scene for each template so we can render a
 * real SVG preview without pulling in the full @excalidraw library.
 */
function buildTemplateScene(name) {
  const mk = (id, type, x, y, w, h, extra = {}) => ({
    id, type, x, y, width: w, height: h, angle: 0,
    strokeColor: '#1e1e1e', backgroundColor: '#ffffff',
    fillStyle: 'solid', strokeWidth: 2, strokeStyle: 'solid',
    roughness: 1, opacity: 100, groupIds: [], frameId: null,
    roundness: type === 'rectangle' ? { type: 3 } : null,
    seed: 1, version: 1, versionNonce: 0, isDeleted: false,
    boundElements: null, updated: 1, link: null, locked: false,
    ...extra,
  });
  const txt = (id, x, y, text, containerId = null, fontSize = 18, w = 100, h = 24) => mk(id, 'text', x, y, w, h, {
    text, fontSize, fontFamily: hasCjk(text) ? 11 : 1, textAlign: 'center', verticalAlign: 'middle',
    containerId, originalText: text, lineHeight: 1.25,
    customData: {
      cjkFontFamily: CJK_FONT_FAMILY,
      cjkFontFallbacks: CJK_FONT_FALLBACKS,
    },
  });
  const arrow = (id, x, y, pts, startId, endId) => ({
    id, type: 'arrow', x, y,
    width: Math.max(...pts.map((point) => point[0])) - Math.min(...pts.map((point) => point[0])),
    height: Math.max(...pts.map((point) => point[1])) - Math.min(...pts.map((point) => point[1])),
    angle: 0,
    strokeColor: '#868e96', backgroundColor: 'transparent',
    fillStyle: 'solid', strokeWidth: 2, strokeStyle: 'solid',
    roughness: 1, opacity: 100, groupIds: [], frameId: null,
    roundness: { type: 2 }, seed: 1, version: 1, versionNonce: 0,
    isDeleted: false, boundElements: null, updated: 1, link: null, locked: false,
    points: pts,
    startBinding: { elementId: startId, focus: 0.5, gap: 0 },
    endBinding: { elementId: endId, focus: 0.5, gap: 0 },
    startArrowhead: null, endArrowhead: 'arrow',
  });

  switch (name) {
    case 'flowchart': {
      const e = [
        mk('s', 'ellipse', 100, 60, 120, 60, { backgroundColor: '#a5d8ff' }),
        txt('ts', 120, 78, '开始', 's', 18, 80),
        mk('p', 'rectangle', 90, 180, 140, 60),
        txt('tp', 100, 198, '处理', 'p', 18, 120),
        mk('d', 'diamond', 80, 300, 160, 80, { backgroundColor: '#fff3bf' }),
        txt('td', 110, 328, '成功?', 'd', 16, 100),
        mk('e', 'ellipse', 100, 440, 120, 60, { backgroundColor: '#b2f2bb' }),
        txt('te', 120, 458, '完成', 'e', 18, 80),
        arrow('a1', 160, 120, [[0, 0], [0, 60]], 's', 'p'),
        arrow('a2', 160, 240, [[0, 0], [0, 60]], 'p', 'd'),
        arrow('a3', 160, 380, [[0, 0], [0, 60]], 'd', 'e'),
      ];
      return { elements: e };
    }
    case 'architecture': {
      const e = [
        mk('f1', 'frame', 40, 40, 420, 90, { backgroundColor: '#dbe4ff', opacity: 30, name: '用户层' }),
        mk('f2', 'frame', 40, 180, 420, 90, { backgroundColor: '#e5dbff', opacity: 30, name: '应用层' }),
        mk('f3', 'frame', 40, 320, 420, 90, { backgroundColor: '#d3f9d8', opacity: 30, name: '数据层' }),
        mk('w', 'rectangle', 80, 60, 140, 50, { backgroundColor: '#a5d8ff', frameId: 'f1' }),
        txt('tw', 95, 74, 'Web', 'w', 16, 110),
        mk('a', 'rectangle', 260, 60, 140, 50, { backgroundColor: '#a5d8ff', frameId: 'f1' }),
        txt('ta', 275, 74, 'API', 'a', 16, 110),
        mk('s', 'rectangle', 160, 200, 160, 50, { backgroundColor: '#d0bfff', frameId: 'f2' }),
        txt('ts', 180, 214, '服务', 's', 16, 120),
        mk('db', 'ellipse', 170, 340, 140, 50, { backgroundColor: '#c3fae8', frameId: 'f3' }),
        txt('tdb', 190, 352, '数据库', 'db', 16, 100),
        arrow('l1', 240, 130, [[0, 0], [0, 50]], 'w', 's'),
        arrow('l2', 240, 270, [[0, 0], [0, 50]], 's', 'db'),
      ];
      return { elements: e };
    }
    case 'sequence': {
      const e = [
        mk('a1', 'rectangle', 80, 40, 100, 40, { backgroundColor: '#a5d8ff' }),
        txt('ta1', 90, 49, '用户', 'a1', 16, 80),
        mk('a2', 'rectangle', 300, 40, 100, 40, { backgroundColor: '#d0bfff' }),
        txt('ta2', 310, 49, '服务', 'a2', 16, 80),
        mk('a3', 'rectangle', 520, 40, 100, 40, { backgroundColor: '#c3fae8' }),
        txt('ta3', 530, 49, '数据库', 'a3', 16, 80),
        mk('l1', 'line', 130, 80, 0, 260, { strokeStyle: 'dashed', strokeWidth: 1, opacity: 60, roughness: 0, points: [[0, 0], [0, 260]] }),
        mk('l2', 'line', 350, 80, 0, 260, { strokeStyle: 'dashed', strokeWidth: 1, opacity: 60, roughness: 0, points: [[0, 0], [0, 260]] }),
        mk('l3', 'line', 570, 80, 0, 260, { strokeStyle: 'dashed', strokeWidth: 1, opacity: 60, roughness: 0, points: [[0, 0], [0, 260]] }),
        arrow('m1', 130, 120, [[0, 0], [220, 0]], 'a1', 'a2'),
        txt('tm1', 180, 96, '1. 请求', null, 13, 90),
        arrow('m2', 350, 180, [[0, 0], [220, 0]], 'a2', 'a3'),
        txt('tm2', 400, 156, '2. 查询', null, 13, 90),
        arrow('m3', 570, 240, [[0, 0], [-220, 0]], 'a3', 'a2'),
        txt('tm3', 400, 216, '3. 返回', null, 13, 90),
      ];
      return { elements: e };
    }
    case 'mindmap': {
      const e = [
        mk('c', 'ellipse', 220, 140, 120, 60, { backgroundColor: '#a5d8ff' }),
        txt('tc', 240, 158, '主题', 'c', 18, 80),
        mk('b1', 'rectangle', 60, 80, 120, 50, { backgroundColor: '#d0bfff' }),
        txt('tb1', 75, 94, '分支A', 'b1', 16, 90),
        mk('b2', 'rectangle', 60, 200, 120, 50, { backgroundColor: '#d0bfff' }),
        txt('tb2', 75, 214, '分支B', 'b2', 16, 90),
        mk('b3', 'rectangle', 400, 80, 120, 50, { backgroundColor: '#d0bfff' }),
        txt('tb3', 415, 94, '分支C', 'b3', 16, 90),
        mk('b4', 'rectangle', 400, 200, 120, 50, { backgroundColor: '#d0bfff' }),
        txt('tb4', 415, 214, '分支D', 'b4', 16, 90),
        arrow('m1', 180, 115, [[0, 0], [-60, -20]], 'c', 'b1'),
        arrow('m2', 180, 175, [[0, 0], [-60, 20]], 'c', 'b2'),
        arrow('m3', 340, 115, [[0, 0], [60, -20]], 'c', 'b3'),
        arrow('m4', 340, 175, [[0, 0], [60, 20]], 'c', 'b4'),
      ];
      return { elements: e };
    }
    case 'swimlane': {
      const e = [
        mk('s1', 'frame', 40, 40, 440, 100, { backgroundColor: '#dbe4ff', opacity: 30, name: '销售' }),
        mk('s2', 'frame', 40, 160, 440, 100, { backgroundColor: '#e5dbff', opacity: 30, name: '运营' }),
        mk('s3', 'frame', 40, 280, 440, 100, { backgroundColor: '#d3f9d8', opacity: 30, name: '财务' }),
        mk('n1', 'rectangle', 90, 70, 140, 50, { frameId: 's1', backgroundColor: '#a5d8ff' }),
        txt('tn1', 105, 84, '接单', 'n1', 16, 110),
        mk('n2', 'rectangle', 300, 70, 140, 50, { frameId: 's1', backgroundColor: '#a5d8ff' }),
        txt('tn2', 315, 84, '确认', 'n2', 16, 110),
        mk('n3', 'rectangle', 160, 190, 160, 50, { frameId: 's2', backgroundColor: '#d0bfff' }),
        txt('tn3', 180, 204, '执行', 'n3', 16, 120),
        mk('n4', 'rectangle', 160, 310, 160, 50, { frameId: 's3', backgroundColor: '#c3fae8' }),
        txt('tn4', 180, 324, '结算', 'n4', 16, 120),
        arrow('e1', 230, 120, [[0, 0], [70, 0]], 'n1', 'n2'),
        arrow('e2', 370, 120, [[0, 0], [0, 70]], 'n2', 'n3'),
        arrow('e3', 240, 240, [[0, 0], [0, 70]], 'n3', 'n4'),
      ];
      return { elements: e };
    }
    case 'erd': {
      const e = [
        mk('u', 'rectangle', 60, 60, 160, 70, { backgroundColor: '#a5d8ff' }),
        txt('tu', 75, 86, '用户', 'u', 18, 130),
        mk('r', 'diamond', 250, 65, 140, 60, { backgroundColor: '#fff3bf' }),
        txt('tr', 285, 86, '拥有', 'r', 16, 70),
        mk('o', 'rectangle', 420, 60, 160, 70, { backgroundColor: '#b2f2bb' }),
        txt('to', 435, 86, '订单', 'o', 18, 130),
        arrow('e1', 220, 95, [[0, 0], [30, 0]], 'u', 'r'),
        arrow('e2', 390, 95, [[0, 0], [30, 0]], 'r', 'o'),
        txt('c1', 190, 140, '1', null, 13, 20),
        txt('c2', 380, 140, 'N', null, 13, 20),
      ];
      return { elements: e };
    }
    case 'hierarchy': {
      const e = [
        mk('root', 'rectangle', 170, 40, 160, 50, { backgroundColor: '#a5d8ff' }),
        txt('troot', 190, 54, '根节点', 'root', 16, 120),
        mk('c1', 'rectangle', 50, 160, 140, 50, { backgroundColor: '#d0bfff' }),
        txt('tc1', 65, 174, '子节点A', 'c1', 16, 110),
        mk('c2', 'rectangle', 230, 160, 140, 50, { backgroundColor: '#d0bfff' }),
        txt('tc2', 245, 174, '子节点B', 'c2', 16, 110),
        mk('c3', 'rectangle', 410, 160, 140, 50, { backgroundColor: '#d0bfff' }),
        txt('tc3', 425, 174, '子节点C', 'c3', 16, 110),
        arrow('h1', 210, 90, [[0, 0], [-60, 70]], 'root', 'c1'),
        arrow('h2', 250, 90, [[0, 0], [0, 70]], 'root', 'c2'),
        arrow('h3', 290, 90, [[0, 0], [60, 70]], 'root', 'c3'),
      ];
      return { elements: e };
    }
    case 'relationship': {
      const e = [
        mk('n1', 'ellipse', 60, 140, 120, 60, { backgroundColor: '#a5d8ff' }),
        txt('tn1', 75, 158, 'A', 'n1', 18, 90),
        mk('n2', 'ellipse', 240, 60, 120, 60, { backgroundColor: '#d0bfff' }),
        txt('tn2', 255, 78, 'B', 'n2', 18, 90),
        mk('n3', 'ellipse', 240, 220, 120, 60, { backgroundColor: '#b2f2bb' }),
        txt('tn3', 255, 238, 'C', 'n3', 18, 90),
        mk('n4', 'ellipse', 420, 140, 120, 60, { backgroundColor: '#ffd8a8' }),
        txt('tn4', 435, 158, 'D', 'n4', 18, 90),
        arrow('r1', 180, 140, [[0, 0], [60, -50]], 'n1', 'n2'),
        arrow('r2', 180, 180, [[0, 0], [60, 50]], 'n1', 'n3'),
        arrow('r3', 360, 140, [[0, 0], [60, 0]], 'n3', 'n4'),
      ];
      return { elements: e };
    }
    case 'comparison': {
      const e = [
        mk('ha', 'rectangle', 60, 60, 180, 40, { backgroundColor: '#a5d8ff' }),
        txt('tha', 90, 70, '方案A', 'ha', 16, 120),
        mk('hb', 'rectangle', 280, 60, 180, 40, { backgroundColor: '#d0bfff' }),
        txt('thb', 310, 70, '方案B', 'hb', 16, 120),
        mk('sep', 'line', 260, 60, 0, 200, { strokeStyle: 'dashed', strokeWidth: 1, opacity: 50, roughness: 0, points: [[0, 0], [0, 200]] }),
        txt('la', 10, 130, '性能', null, 15, 60),
        txt('va', 100, 130, '高吞吐', null, 14, 100),
        txt('vb', 320, 130, '中等', null, 14, 100),
        txt('lb', 10, 180, '成本', null, 15, 60),
        txt('va2', 100, 180, '较低', null, 14, 100),
        txt('vb2', 320, 180, '较高', null, 14, 100),
      ];
      return { elements: e };
    }
    case 'timeline': {
      const e = [
        txt('t', 170, 30, '项目里程碑', null, 20, 180),
        mk('axis', 'line', 60, 100, 440, 0, { strokeWidth: 3, roughness: 1, points: [[0, 0], [440, 0]] }),
        mk('m1', 'line', 100, 90, 0, 20, { strokeWidth: 2, points: [[0, 0], [0, 20]] }),
        mk('d1', 'ellipse', 93, 83, 14, 14, { backgroundColor: '#a5d8ff' }),
        mk('m2', 'line', 220, 90, 0, 20, { strokeWidth: 2, points: [[0, 0], [0, 20]] }),
        mk('d2', 'ellipse', 213, 83, 14, 14, { backgroundColor: '#d0bfff' }),
        mk('m3', 'line', 340, 90, 0, 20, { strokeWidth: 2, points: [[0, 0], [0, 20]] }),
        mk('d3', 'ellipse', 333, 83, 14, 14, { backgroundColor: '#b2f2bb' }),
        mk('m4', 'line', 460, 90, 0, 20, { strokeWidth: 2, points: [[0, 0], [0, 20]] }),
        mk('d4', 'ellipse', 453, 83, 14, 14, { backgroundColor: '#ffd8a8' }),
        txt('ev1', 75, 130, 'Q1', null, 13, 60),
        txt('ev2', 195, 130, 'Q2', null, 13, 60),
        txt('ev3', 315, 130, 'Q3', null, 13, 60),
        txt('ev4', 435, 130, 'Q4', null, 13, 60),
      ];
      return { elements: e };
    }
    default:
      return { elements: [] };
  }
}

function previewTemplate(name, outDir) {
  const names = name === '--all' ? Object.keys(TEMPLATES) : [name];
  for (const key of names) {
    const tmpl = TEMPLATES[key];
    if (!tmpl) {
      console.error(`未找到模板: ${key}`);
      console.error(`可用模板: ${Object.keys(TEMPLATES).join(', ')}`);
      process.exit(1);
    }
    console.log(`  ${tmpl.name}`);
    console.log(`  ${'-'.repeat(40)}`);
    console.log(`  描述: ${tmpl.description}`);
    console.log(`  布局: ${tmpl.layout}`);
    console.log(`  复杂度: ${tmpl.complexity}`);
    console.log(`  使用元素: ${tmpl.elements.join(', ')}`);
    console.log(`  适用场景: ${tmpl.scenes.join(', ')}`);
    console.log(`  色板: ${JSON.stringify(tmpl.colors)}`);
    console.log(`  参考文件: references/diagram-templates.md (第 ${getTemplateSection(key)} 节)`);
    if (svgRenderer) {
      const scene = buildTemplateScene(key);
      const { svg } = svgRenderer.renderSvgFromScene(
        {
          type: 'excalidraw', version: 2, elements: scene.elements,
          appState: {
            viewBackgroundColor: '#ffffff',
            cjkFontFamily: CJK_FONT_FAMILY,
            cjkFontFallbacks: CJK_FONT_FALLBACKS,
          },
        },
        { padding: 40 }
      );
      const targetDir = outDir || 'output/template-previews';
      fs.mkdirSync(targetDir, { recursive: true });
      const outFile = path.join(targetDir, `${key}.svg`);
      fs.writeFileSync(outFile, svg);
      console.log(`  SVG 预览: ${outFile}`);
    } else {
      console.log('  (SVG 渲染器不可用，跳过预览渲染)');
    }
    console.log();
  }
}

function getTemplateSection(name) {
  const sections = {
    flowchart: 1, architecture: 2, sequence: 3, mindmap: 4,
    swimlane: 5, erd: 6, hierarchy: 7, relationship: 8,
    comparison: 9, timeline: 10
  };
  return sections[name] || '?';
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const format = args.includes('--json') ? 'json' : 'text';

  if (args.includes('--preview')) {
    const idx = args.indexOf('--preview');
    const target = idx + 1 < args.length && !args[idx + 1].startsWith('--') ? args[idx + 1] : null;
    const outIdx = args.indexOf('--out');
    const outDir = outIdx >= 0 && outIdx + 1 < args.length ? args[outIdx + 1] : null;
    previewTemplate(target || '--all', outDir);
  } else {
    listTemplates(format);
  }
}

module.exports = { TEMPLATES, THEMES, buildTemplateScene };
