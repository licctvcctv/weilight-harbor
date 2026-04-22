const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber } = require("docx");

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerShading = { fill: "E8F0FE", type: ShadingType.CLEAR };

function headerCell(text, width) {
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    shading: headerShading, verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, bold: true, size: 21, font: "Microsoft YaHei" })] })]
  });
}

function cell(texts, width, opts = {}) {
  const children = Array.isArray(texts) ? texts : [texts];
  const paragraphs = children.map(t => {
    if (typeof t === "object" && t.type === "paragraph") return t;
    return new Paragraph({ children: [new TextRun({ text: String(t), size: 21, font: "Microsoft YaHei", ...opts })] });
  });
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER, children: paragraphs
  });
}

function codeBlock(lines) {
  return lines.map(line => new Paragraph({
    spacing: { before: 20, after: 20 },
    shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
    indent: { left: 360 },
    children: [new TextRun({ text: line, font: "Consolas", size: 18, color: "333333" })]
  }));
}

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: opts.spacingBefore || 80, after: opts.spacingAfter || 80 },
    indent: opts.indent ? { left: opts.indent } : undefined,
    children: Array.isArray(text) ? text : [new TextRun({ text, size: 22, font: "Microsoft YaHei", ...opts })]
  });
}

function bold(text) { return new TextRun({ text, bold: true, size: 22, font: "Microsoft YaHei" }); }
function normal(text) { return new TextRun({ text, size: 22, font: "Microsoft YaHei" }); }
function code(text) { return new TextRun({ text, font: "Consolas", size: 20, color: "C7254E" }); }
function hr() { return new Paragraph({ spacing: { before: 200, after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC", space: 8 } }, children: [] }); }

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Microsoft YaHei", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 44, bold: true, color: "1A1A1A", font: "Microsoft YaHei" },
        paragraph: { spacing: { before: 240, after: 200 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "1A5276", font: "Microsoft YaHei" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "2E4057", font: "Microsoft YaHei" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "34495E", font: "Microsoft YaHei" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullet", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullet2", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 360 } } } }] },
      { reference: "num-solution1", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "num-solution2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "num-solution3", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "num-solution4", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "num-test", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "num-test2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "num-test3", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "num-flow", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Weilight Harbor - Dev Q&A", size: 18, color: "999999", font: "Microsoft YaHei" })] })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Page ", size: 18, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "999999" }), new TextRun({ text: " / ", size: 18, color: "999999" }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: "999999" })] })] })
    },
    children: [
      // Title
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: "微光港湾（Weilight Harbor）", font: "Microsoft YaHei" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [new TextRun({ text: "开发问答", size: 32, color: "555555", font: "Microsoft YaHei" })] }),

      hr(),

      // ===== Section 1: Challenges =====
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("一、写代码过程中遇到了什么挑战？是怎么解决的？")] }),

      // Challenge 1
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("挑战 1：敏感词检测系统的设计与性能优化")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("问题描述")] }),
      p("社区是面向重病患者家属的情感支持平台，用户可能在帖子中表达极度负面情绪甚至自伤倾向。我们需要同时实现两种完全不同的内容审核逻辑："),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("危机级别"), normal('\uff08\u5982\u201c\u81ea\u6740\u201d\u201c\u4e0d\u60f3\u6d3b\u201d\u7b49\u81ea\u4f24\u5173\u952e\u8bcd\uff09\uff1a\u9700\u8981'), bold("\u7acb\u5373\u5f39\u51fa\u5371\u673a\u70ed\u7ebf\u5f39\u7a97"), normal("\uff0c\u7ed9\u7528\u6237\u63d0\u4f9b\u5fc3\u7406\u63f4\u52a9\u8d44\u6e90\uff0c\u800c\u4e0d\u662f\u7b80\u5355\u5730\u5c4f\u853d\u5185\u5bb9\u3002")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("普通敏感词"), normal("\uff08\u5982\u8fb1\u9a82\u3001\u8bc8\u9a97\u76f8\u5173\u8bcd\u6c47\uff09\uff1a\u9700\u8981\u5c06\u5e16\u5b50"), bold("\u81ea\u52a8\u9690\u85cf\u4e3a\u5f85\u5ba1\u6838\u72b6\u6001"), normal("\uff0c\u7b49\u7ba1\u7406\u5458\u5ba1\u6838\u540e\u518d\u51b3\u5b9a\u662f\u5426\u53d1\u5e03\u3002")] }),
      p("同时，敏感词检测在多个功能模块中被调用（社区发帖、评论、深夜独白、实时输入检测 API），如果每次都查询数据库，会造成性能瓶颈。"),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("解决方案")] }),
      new Paragraph({ numbering: { reference: "num-solution1", level: 0 }, children: [bold("分级严重度模型"), normal("：在数据库中为每个敏感词设置 severity 字段（1=警告级，2=危机级）。检测逻辑根据严重度返回不同响应：")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("severity \u2265 2 \u2192 前端弹出包含心理援助热线的温暖弹窗，不提交内容")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("severity \u2265 1 \u2192 帖子以 status=0（隐藏）状态入库，等待管理员审核")] }),
      new Paragraph({ numbering: { reference: "num-solution1", level: 0 }, children: [bold("内存缓存机制"), normal("：实现了带 5 分钟 TTL（生存时间）的内存缓存，敏感词列表从数据库懒加载后缓存在内存中，避免每次请求都查询数据库。缓存过期后自动重新加载。")] }),
      new Paragraph({ numbering: { reference: "num-solution1", level: 0 }, children: [bold("前端实时检测"), normal("：提供了 /community/check-sensitive API 接口，前端使用 800ms 防抖（debounce）机制在用户输入时实时调用，实现\u201c边输入边检测\u201d的体验，同时避免频繁请求服务器。")] }),
      new Paragraph({ numbering: { reference: "num-solution1", level: 0 }, children: [bold("差异化处理"), normal("：不同模块对检测结果的处理方式不同：")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("发帖：隐藏待审核（软处理，不丢失用户内容）")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("评论：直接阻止提交（严格处理）")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("深夜独白：危机词返回 JSON 标记，前端显示关怀弹窗")] }),

      hr(),

      // Challenge 2
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("挑战 2：深夜独白功能的时间限制与匿名机制")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("问题描述")] }),
      p("深夜独白（Night Confessions）是一个特色功能——只在晚上 21:00 到凌晨 6:00 开放，完全匿名，让用户在深夜说出白天不敢说的话。实现这个功能遇到了几个技术难点："),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("如何在前端和后端同时控制时间窗口？")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("匿名用户没有登录账号，如何追踪同一个用户的多条独白？")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("如何生成不重复且有温度的匿名昵称？")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("解决方案")] }),
      new Paragraph({ numbering: { reference: "num-solution2", level: 0 }, children: [bold("双层时间验证"), normal("：")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("前端：页面加载时检测当前时间，非开放时段显示倒计时和\u201c月亮休息中\u201d的提示动画")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("后端：POST 接口再次验证服务器时间（UTC 21:00-06:00），防止用户通过修改本地时间绕过限制")] }),
      new Paragraph({ numbering: { reference: "num-solution2", level: 0 }, children: [bold("Session ID 追踪"), normal("：为未登录用户生成唯一的 session ID，存储在浏览器 session 中。这样即使用户没有登录，系统也能识别同一个浏览器会话发出的多条独白，为后续功能（如限流）提供基础。")] }),
      new Paragraph({ numbering: { reference: "num-solution2", level: 0 }, children: [bold("随机动物昵称"), normal("：预设了一组有温度的匿名昵称（萤火虫 Firefly、星雀 Starling 等），每条独白随机分配一个。虽然理论上存在昵称碰撞的可能，但在当前用户量级下概率极低，且碰撞本身不影响功能。")] }),

      hr(),

      // Challenge 3
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("挑战 3：喘息驿站的地图交互与移动端适配")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("问题描述")] }),
      p("喘息驿站需要在地图上展示求助请求和器械出借信息，用户可以按距离筛选、点击标记查看详情、发布和接单。这在桌面端用 Leaflet.js + 侧栏列表的方案比较成熟，但在移动端小屏幕上同时展示地图和列表非常困难。"),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("解决方案")] }),
      new Paragraph({ numbering: { reference: "num-solution3", level: 0 }, children: [bold("响应式双布局"), normal("：")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("桌面端：左侧列表（可收起/展开）+ 右侧地图的经典分栏布局")] }),
      new Paragraph({ numbering: { reference: "bullet2", level: 0 }, children: [normal("移动端：全屏地图 + 底部弹窗（bottom sheet）替代侧栏，用户上滑查看列表")] }),
      new Paragraph({ numbering: { reference: "num-solution3", level: 0 }, children: [bold("标记聚合"), normal("：使用 Leaflet.markercluster 插件，在缩小地图时自动将密集的标记聚合为数字气泡，避免标记重叠导致的视觉混乱。")] }),
      new Paragraph({ numbering: { reference: "num-solution3", level: 0 }, children: [bold("颜色编码与脉冲动画"), normal("：橙色标记=求助服务，绿色标记=器械出借；待响应的请求有脉冲动画效果，让用户一眼区分紧急程度。")] }),
      new Paragraph({ numbering: { reference: "num-solution3", level: 0 }, children: [bold("半径预设"), normal("：提供 3km/5km/10km/20km 快捷按钮，点击后地图自动缩放到对应范围，比手动缩放更直观。")] }),

      hr(),

      // Challenge 4
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("挑战 4：管理后台与前台系统的整合")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("问题描述")] }),
      p("我们的管理后台基于 pear-admin-flask（一个基于 Layui 的 Flask 管理后台框架），但前台是用 Bootstrap 5 + 自定义暖色主题构建的。两套 UI 框架并存带来了："),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("路由命名空间冲突")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("模板继承链不同（Layui layout vs Bootstrap layout）")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("用户认证系统需要同时服务前台普通用户和后台管理员")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("解决方案")] }),
      new Paragraph({ numbering: { reference: "num-solution4", level: 0 }, children: [bold("蓝图（Blueprint）隔离"), normal("：将管理后台的认证审核、筹款审核、社区审核分别注册为独立的 Flask Blueprint，URL 统一以 /admin/ 开头，与前台路由完全隔离。")] }),
      new Paragraph({ numbering: { reference: "num-solution4", level: 0 }, children: [bold("权限装饰器"), normal("：使用 @authorize(\"权限代码\", log=True) 装饰器保护所有管理后台路由，基于 RBAC（基于角色的访问控制）模型，只有管理员角色才能访问后台功能。")] }),
      new Paragraph({ numbering: { reference: "num-solution4", level: 0 }, children: [bold("双模板目录"), normal("：前台模板放在 templates/ 下使用 Bootstrap 布局，管理后台模板放在 templates/admin/ 下使用 Layui 布局，通过不同的 {% extends %} 基类彻底分离。")] }),
      new Paragraph({ numbering: { reference: "num-solution4", level: 0 }, children: [bold("统一用户模型"), normal("：前台用户和管理员共用同一个 User 模型，通过 role 关联表区分权限，避免维护两套用户表。")] }),

      hr(),

      // ===== Section 2: Sensitive Words =====
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("二、敏感词检测具体有哪些词？")] }),
      p([normal("敏感词分为两个级别，共 "), bold("15 个词"), normal("：")]),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("危机级别（Severity 2）—— 触发心理援助弹窗")] }),
      new Table({
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ tableHeader: true, children: [headerCell("中文", 4680), headerCell("英文", 4680)] }),
          new TableRow({ children: [cell("自杀", 4680), cell("suicide", 4680)] }),
          new TableRow({ children: [cell("不想活", 4680), cell("kill myself", 4680)] }),
          new TableRow({ children: [cell("结束生命", 4680), cell("end my life", 4680)] }),
          new TableRow({ children: [cell("活不下去", 4680), cell("want to die", 4680)] }),
          new TableRow({ children: [cell("轻生", 4680), cell("no reason to live", 4680)] }),
        ]
      }),
      p([normal("检测到这些词时，前端会弹出温暖的危机干预弹窗，显示心理援助热线号码，内容"), bold("不会被提交"), normal("。")], { spacingBefore: 160 }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("警告级别（Severity 1）—— 帖子自动隐藏待审核")] }),
      new Table({
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ tableHeader: true, children: [headerCell("中文", 4680), headerCell("英文", 4680)] }),
          new TableRow({ children: [cell("骗子", 4680), cell("scam", 4680)] }),
          new TableRow({ children: [cell("诈骗", 4680), cell("fraud", 4680)] }),
          new TableRow({ children: [cell("傻逼", 4680), cell("damn", 4680)] }),
          new TableRow({ children: [cell("\u2014", 4680), cell("stupid", 4680)] }),
          new TableRow({ children: [cell("\u2014", 4680), cell("idiot", 4680)] }),
        ]
      }),
      p("检测到这些词时，帖子会以隐藏状态（status=0）保存到数据库，等待管理员在后台审核后决定是否公开。", { spacingBefore: 160 }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("检测机制说明")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("匹配方式"), normal("：大小写不敏感的子字符串匹配（如输入\"SUICIDE\"也会被检测到）")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("检测范围"), normal("：标题 + 正文合并检测")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("缓存策略"), normal("：词库从数据库加载后缓存 5 分钟，避免频繁查询")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("管理方式"), normal("：目前通过 flask seed 命令初始化词库，后续可在管理后台扩展管理界面")] }),

      hr(),

      // ===== Section 3: Admin Panel =====
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("三、管理者面板（Admin Panel）是不是还在完成？")] }),
      p([bold("管理后台已经完成。"), normal(" 以下是已实现的全部功能：")]),

      new Table({
        columnWidths: [2200, 4960, 2200],
        rows: [
          new TableRow({ tableHeader: true, children: [headerCell("模块", 2200), headerCell("功能", 4960), headerCell("状态", 2200)] }),
          new TableRow({ children: [cell("认证审核", 2200, { bold: true }), cell("查看用户提交的认证申请、审核材料、通过/驳回（需填写驳回理由）", 4960), cell("\u2705 已完成", 2200)] }),
          new TableRow({ children: [cell("筹款审核", 2200, { bold: true }), cell("查看筹款项目详情、封面、收款码，审核通过/驳回", 4960), cell("\u2705 已完成", 2200)] }),
          new TableRow({ children: [cell("社区审核", 2200, { bold: true }), cell("查看被敏感词拦截的帖子，可通过/隐藏/删除", 4960), cell("\u2705 已完成", 2200)] }),
          new TableRow({ children: [cell("用户管理", 2200, { bold: true }), cell("查看所有用户、编辑用户信息、启用/禁用账号", 4960), cell("\u2705 已完成", 2200)] }),
          new TableRow({ children: [cell("角色权限管理", 2200, { bold: true }), cell("RBAC 权限系统，角色分配、权限配置", 4960), cell("\u2705 已完成", 2200)] }),
          new TableRow({ children: [cell("操作日志", 2200, { bold: true }), cell("记录所有管理员操作的审计日志", 4960), cell("\u2705 已完成", 2200)] }),
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("访问方式")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("地址"), normal("：http://csi6220-2-vm3.ucd.ie/admin/（或本地 http://localhost:5000/admin/）")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("账号"), normal("：admin")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [bold("密码"), normal("：admin123")] }),
      p("登录后可以看到左侧菜单，包含认证审核、筹款审核、社区审核等入口。"),

      hr(),

      // ===== Section 4: Testing =====
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("四、敏感词要怎么测试？")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("方法 1：在社区发帖测试（最直观）")] }),
      new Paragraph({ numbering: { reference: "num-test", level: 0 }, children: [normal("登录任意账号（如 limei / test123）")] }),
      new Paragraph({ numbering: { reference: "num-test", level: 0 }, children: [normal("进入"), bold("共鸣社区"), normal("页面，点击\u201c发帖\u201d")] }),
      new Paragraph({ numbering: { reference: "num-test", level: 0 }, children: [normal("在帖子内容中输入包含敏感词的文字：")] }),
      p([bold("测试危机级别（弹窗效果）：")], { spacingBefore: 160 }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("输入\u201c我不想活了\u201d或\u201csuicide\u201d")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("预期结果：弹出温暖的危机干预弹窗，显示心理援助热线，内容不会被提交")] }),
      p([bold("测试警告级别（隐藏待审核）：")], { spacingBefore: 160 }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("输入\u201c这个骗子\u201d或\u201cscam\u201d")] }),
      new Paragraph({ numbering: { reference: "bullet", level: 0 }, children: [normal("预期结果：帖子成功提交，但提示\u201c内容待审核\u201d，帖子以隐藏状态存入数据库")] }),
      new Paragraph({ numbering: { reference: "num-test", level: 0 }, children: [normal("登录管理后台（admin / admin123），进入"), bold("社区审核"), normal("模块，可以看到被拦截的帖子，管理员可以选择通过或删除。")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("方法 2：在深夜独白测试")] }),
      new Paragraph({ numbering: { reference: "num-test2", level: 0 }, children: [normal("在晚上 21:00 之后访问共鸣社区页面（右侧深夜独白区域会亮起）")] }),
      new Paragraph({ numbering: { reference: "num-test2", level: 0 }, children: [normal("输入包含危机关键词的内容（如\u201c我想结束生命\u201d）")] }),
      new Paragraph({ numbering: { reference: "num-test2", level: 0 }, children: [normal("预期结果：弹出关怀弹窗，显示支持信息和热线号码")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("方法 3：实时输入检测（API 测试）")] }),
      p("在社区发帖的输入框中慢慢输入敏感词，输入停顿约 800ms 后，系统会通过 AJAX 调用 /community/check-sensitive 接口进行实时检测，如果是危机级别词汇，会立即弹出提示。"),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("方法 4：通过命令行测试（开发者）")] }),
      ...codeBlock([
        "# 进入项目目录",
        "cd weilight-harbor",
        "",
        "# 激活虚拟环境",
        "source venv/bin/activate",
        "",
        "# 进入 Flask shell",
        "flask shell",
        "",
        "# 测试敏感词检测",
        "from applications.common.utils.sensitive import check_sensitive, has_crisis_words",
        "",
        "# 测试普通敏感词",
        "print(check_sensitive(\"这个骗子太可恶了\"))",
        "# 输出: [{'word': '骗子', 'severity': 1}]",
        "",
        "# 测试危机词汇",
        "print(check_sensitive(\"我不想活了\"))",
        "# 输出: [{'word': '不想活', 'severity': 2}]",
        "",
        "# 检查是否包含危机词",
        "print(has_crisis_words(\"我想自杀\"))",
        "# 输出: True",
        "",
        "# 正常内容",
        "print(check_sensitive(\"今天天气真好\"))",
        "# 输出: []",
      ]),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("完整测试流程建议")] }),
      new Paragraph({ numbering: { reference: "num-flow", level: 0 }, children: [bold("先测试正常发帖"), normal("：发一条不含敏感词的帖子 \u2192 应立即可见")] }),
      new Paragraph({ numbering: { reference: "num-flow", level: 0 }, children: [bold("测试警告级敏感词"), normal("：发一条包含\u201c骗子\u201d的帖子 \u2192 应提示待审核")] }),
      new Paragraph({ numbering: { reference: "num-flow", level: 0 }, children: [bold("测试危机级敏感词"), normal("：输入\u201c不想活\u201d \u2192 应弹出危机热线弹窗")] }),
      new Paragraph({ numbering: { reference: "num-flow", level: 0 }, children: [bold("管理后台审核"), normal("：登录 admin 后台 \u2192 社区审核 \u2192 可以看到被拦截的帖子 \u2192 通过/隐藏/删除")] }),
      new Paragraph({ numbering: { reference: "num-flow", level: 0 }, children: [bold("通过后验证"), normal("：管理员通过帖子后 \u2192 回到社区页面 \u2192 帖子变为可见")] }),

      hr(),
      p([normal("文档生成日期：2026-04-22")], { spacingBefore: 200 }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/a136/vs/254752425/weilight-harbor/docs/开发问答.docx", buffer);
  console.log("Done: 开发问答.docx");
});
