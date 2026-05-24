(function () {
  var locale = String(window.WL_ADMIN_LOCALE || document.documentElement.lang || 'en').slice(0, 2)
  if (locale !== 'zh') {
    locale = 'en'
  }
  document.documentElement.lang = locale

  var copy = {
    en: {
      go: 'Go',
      goTo: 'Go to',
      page: 'page',
      total: 'Total',
      perPage: '/ page'
    },
    zh: {
      go: '确定',
      goTo: '到第',
      page: '页',
      total: '共',
      perPage: '条/页'
    }
  }[locale]

  function replaceTextNode(node, replacer) {
    Array.prototype.forEach.call(node.childNodes || [], function (child) {
      if (child.nodeType === 3) {
        child.nodeValue = replacer(child.nodeValue)
      }
    })
  }

  function patchPagination(root) {
    if (locale !== 'en') {
      return
    }
    var scope = root || document
    var counts = scope.querySelectorAll('.layui-laypage-count')
    Array.prototype.forEach.call(counts, function (node) {
      var match = node.textContent.match(/\d+/)
      if (match) {
        node.textContent = copy.total + ' ' + match[0]
      }
    })

    var skips = scope.querySelectorAll('.layui-laypage-skip')
    Array.prototype.forEach.call(skips, function (node) {
      replaceTextNode(node, function (text) {
        return text.replace(/到第/g, copy.goTo + ' ').replace(/页/g, ' ' + copy.page)
      })
      var button = node.querySelector('button')
      if (button) {
        button.textContent = copy.go
      }
    })

    var limitOptions = scope.querySelectorAll('.layui-laypage-limits select option')
    Array.prototype.forEach.call(limitOptions, function (option) {
      option.textContent = option.textContent.replace(/(\d+)\s*条\/页/g, '$1 ' + copy.perPage)
    })

    var limitInputs = scope.querySelectorAll('.layui-laypage-limits .layui-select-title input')
    Array.prototype.forEach.call(limitInputs, function (input) {
      input.value = input.value.replace(/(\d+)\s*条\/页/g, '$1 ' + copy.perPage)
    })
  }

  function syncFixedColumns(root) {
    var scope = root || document
    var views = scope.querySelectorAll('.layui-table-view')
    Array.prototype.forEach.call(views, function (view) {
      var mainRows = view.querySelectorAll('.layui-table-main tbody tr')
      if (!mainRows.length) {
        return
      }
      Array.prototype.forEach.call(['.layui-table-fixed-r', '.layui-table-fixed-l'], function (fixedSelector) {
        var fixed = view.querySelector(fixedSelector)
        if (!fixed) {
          return
        }
        var fixedRows = fixed.querySelectorAll('.layui-table-body tbody tr')
        Array.prototype.forEach.call(fixedRows, function (row, index) {
          var mainRow = mainRows[index]
          if (!mainRow) {
            return
          }
          var height = Math.ceil(mainRow.getBoundingClientRect().height)
          if (!height) {
            return
          }
          row.style.height = height + 'px'
          Array.prototype.forEach.call(row.querySelectorAll('.layui-table-cell'), function (cell) {
            cell.style.height = Math.max(28, height - 12) + 'px'
            cell.style.lineHeight = '28px'
          })
        })
      })
    })
  }

  function schedulePatch() {
    window.setTimeout(function () { patchPagination(document); syncFixedColumns(document) }, 0)
    window.setTimeout(function () { patchPagination(document); syncFixedColumns(document) }, 80)
    window.setTimeout(function () { patchPagination(document); syncFixedColumns(document) }, 240)
    window.setTimeout(function () { syncFixedColumns(document) }, 600)
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', schedulePatch)
  } else {
    schedulePatch()
  }

  var observer = new MutationObserver(function (mutations) {
    var shouldPatch = mutations.some(function (mutation) {
      return Array.prototype.some.call(mutation.addedNodes || [], function (node) {
        return node.nodeType === 1 && (
          node.classList.contains('layui-table-page') ||
          node.querySelector && node.querySelector('.layui-table-page')
        )
      })
    })
    if (shouldPatch) {
      schedulePatch()
    }
  })

  observer.observe(document.documentElement, { childList: true, subtree: true })
})()
