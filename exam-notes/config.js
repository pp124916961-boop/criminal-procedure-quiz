// 考試筆記頁面設定
// 之後新增一般 JPG 頁面時，只需要：
// 1. 上傳 assets/admin-pages/page-XX.jpg
// 2. 把 total 改成最新總頁數
window.EXAM_NOTES_CONFIG = Object.freeze({
  admin: Object.freeze({
    total: 31,
    directory: 'assets/admin-pages',
    prefix: 'page-',
    defaultExtension: 'jpg',
    // 只有不是一般 JPG 的特殊頁面才需要列在這裡；一般新增頁面不用改 overrides。
    overrides: Object.freeze({
      31: 'page-31.svg'
    })
  })
});
