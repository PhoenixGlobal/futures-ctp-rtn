初始化集群 -> 监听插入

``` bash
# 进入 mongosh
docker exec -it futures-ctp mongosh
```

``` mongosh
# 在 mongosh 里初始化 replica set（允许监听），并设置集群地址
# 其中 ip 改为 docker 所在服务器的 ip

rs.initiate({
  _id: "random_name_cluster",
  members: [
    {
      _id: 0,
      host: "192.168.254.162:10001"
    }
  ]
})
```
