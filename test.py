import context

ctx = context.build()

ctx = ctx.create_tenant('Alcuin2')

ctx.save()
ctx.restore_tenant('Alcuin2')
